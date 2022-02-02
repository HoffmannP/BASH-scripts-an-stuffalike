#!/usr/bin/env python3

import requests
from collections import namedtuple
from sys import argv
import json

Repository = namedtuple('Repository', 'name stars forks last_change')
ENDPOINT = "https://api.github.com/graphql"
AUTH_TOKEN = "***"
GRAPHQL_QUERY = '''query Forks($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    nameWithOwner
    stargazerCount
    forkCount
    object(expression: \"master\") {
      ... on Commit {
        committedDate
        history {
          totalCount
          __typename
        }
        __typename
      }
      __typename
    }
    forks(first: 100, orderBy: {field: STARGAZERS, direction: DESC}) {
      nodes {
        nameWithOwner
        stargazerCount
        forkCount
        object(expression: \"master\") {
          ... on Commit {
            committedDate
            history {
              totalCount
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
'''

def queryGitHub(repository):
    request = {
        'operationName': 'Forks',
        'variables': {
            'owner': repository[0],
            'name': repository[1]
        },
        'query': GRAPHQL_QUERY
    }
    response = requests.post(ENDPOINT, headers={'Authorization': f'Bearer {AUTH_TOKEN}'}, data=json.dumps(request))
    return response.json()

def parseRepository(repro):
    return Repository(
        repro['nameWithOwner'],
        repro['stargazerCount'],
        repro['forkCount'],
        repro['object']['committedDate'])

def fetchChildren(response):
    forks = response['data']['repository']['forks']['nodes']
    repos = []
    for fork in forks:
        repos += [parseRepository(fork)]
        if fork['forkCount'] > 0:
            repos += fetchChildren(queryGitHub(fork['nameWithOwner'].split('/')))
    return repos


response = queryGitHub(argv[1].split('/')[-2:])
base = parseRepository(response['data']['repository'])
repositories = [base]
if base.forks > 0:
    repositories += fetchChildren(response)

r = Repository('Name', 'Stars', 'Forks', 'LastChange')
print(f'{r.name:50s} {r.stars:5s} {r.forks:5s} {r.last_change}')
for r in sorted(repositories, key=lambda a: a.last_change, reverse=True):
    print(f'{r.name:50s} {r.stars:5d} {r.forks:5d} {r.last_change}')