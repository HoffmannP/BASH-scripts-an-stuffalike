#!/bin/bash

BASE_URL='https://synapse.matrix.uni-jena.de'
USERNAME='p2lebe'
PASSWORD='d2DFf0c8vwnca4k0'
SESSION='script'
ROOM='!kHSgIOdamwTwfJckxa:uni-jena.de'
MSG='Dies ist eine Testnachricht'

# TOKEN=$(http -j "$BASE_URL/_matrix/client/r0/login" type=m.login.password user=$USERNAME password=$PASSWORD session=$SESSION | jq -r .access_token)
# echo "Token successfull: $TOKEN"
TOKEN="syt_cDJsZWJl_nOiVZgYJCKGxekMvCLfG_0lNcms"
AUTH="Authorization:Bearer $TOKEN"


# jq -c . <<EOT |
# {
#     "creation_content": {
#         "m.federate": "false"
#     },
#     "room_alias_name": "HS2.streaming.mmz.urz",
#     "name": "Hörsaal 2 Chat",
#     "visibility": "private"
# }
# EOT
# http -j POST "$BASE_URL/_matrix/client/v3/createRoom" "$AUTH"

# echo '{ "filter": { "generic_search_term": "" } }' | http -j POST "$BASE_URL/_matrix/client/v3/publicRooms" "$AUTH" #| jq '.chunk | map([.name, .room_id])'

http "$BASE_URL/_matrix/client/v3/directory/room/%23HS2.streaming.mmz.urz:uni-jena.de"

# http -p bBhH GET "$BASE_URL/_matrix/client/v3/account/whoami" "$AUTH"

# MESSAGE="[$(date)] $MSG"
# http -p bBhH -j "$BASE_URL/_matrix/client/r0/rooms/$ROOM/send/m.room.message" "$AUTH" msgtype=m.text "body=$MESSAGE"
