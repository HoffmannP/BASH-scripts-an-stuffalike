#!/bin/bash

dpkg -l | grep ^ii | tr -s ' ' "\t" | cut -f2 | tee allPackages.txt

rm dependencyList.txt
touch dependencyList.txt
for package in $(cat allPackages.txt); do
	apt-cache -i depends $package | sed -n '/^ .Hängt[^:]*: [^<]/{s/^ .Hängt[^:]*: //;p}' | tee -a dependencyList.txt
done;
sort -u dependencyList.txt | tee dependencyList.tmp.txt
mv dependencyList.tmp.txt dependencyList.txt

rm directPackages.txt
touch directPackages.txt
for package in $(cat allPackages.txt); do
	if [[ $(grep -c $package dependencyList.txt) -eq 0 ]]; then
		echo $package  | tee -a directPackages.txt;
	fi;
done;