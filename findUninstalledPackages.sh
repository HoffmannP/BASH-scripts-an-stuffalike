#!/bin/bash

dpkg -l | grep ^ii | tr -s ' ' "\t" | cut -f2 > packageList.txt

touch dependencyList.txt
for package in $(cat packageList.txt); do
	apt-cache -i depends $package | sed -n '/^  Hängt ab von: [^<]/{s/^  Hängt ab von: //;p}' >> dependencyList.txt
done;
dependencyList.txt | sort -u > dependencyList.tmp.txt
mv dependencyList.tmp.txt dependencyList.txt

touch installedPackages.txt
for package in $(cat packageList.txt); do
	if [[ $(grep -c $package dependencyList.txt) -eq 0 ]]; then
		echo $package >> installedPackages.txt;
	fi;
done;