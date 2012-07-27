#!/bin/bash

dpkg -l | grep ^ii | tr -s ' ' "\t" | cut -f2 | tee packageList.txt

touch dependencyList.txt
for package in $(cat packageList.txt); do
	apt-cache -i depends $package | sed -n '/^ .Hängt[^:]*: [^<]/{s/^ .Hängt[^:]*: //;p}' | tee -a dependencyList.txt
done;
sort -u dependencyList.txt | tee dependencyList.tmp.txt
mv dependencyList.tmp.txt dependencyList.txt

touch installedPackages.txt
for package in $(cat packageList.txt); do
	if [[ $(grep -c $package dependencyList.txt) -eq 0 ]]; then
		echo $package  | tee -a installedPackages.txt;
	fi;
done;