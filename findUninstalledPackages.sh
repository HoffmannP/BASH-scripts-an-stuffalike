#!/bin/bash

if [[ $# -eq 0 ]]; then
	echo '$0 (source|target|compare|explain|install)'
	exit 0
fi

action=$(echo $1 | tr [A-Z] [a-z])
case "$action" in
	"source") # Auf Source Rechner Liste der direkt installierten Pakete
		rm -f allPackages.txt
		dpkg -l | grep ^ii | tr -s ' ' "\t" | cut -f2 | sort | tee allPackages.txt

		rm -f dependencyList.txt
		touch dependencyList.txt
		for package in $(cat allPackages.txt); do
			apt-cache -i depends $package | \
				sed -n '/^ .Hängt[^:]*: [^<]/{s/^ .Hängt[^:]*: //;p}' | \
				tee -a dependencyList.txt
		done
		sort -u dependencyList.txt | tee dependencyList.tmp.txt
		mv dependencyList.tmp.txt dependencyList.txt

		rm -f directPackages.txt
		touch directPackages.txt
		for package in $(cat allPackages.txt); do
			if [[ $(grep -c $package dependencyList.txt) -eq 0 ]]; then
				echo $package | tee -a directPackages.txt
			fi
		done
		;;
	
	"target") # Auf Target Rechner Liste der direkt installierten Pakete
		rm -f allPackages.Name.txt
		dpkg -l | grep ^ii | tr -s ' ' "\t" | cut -f2 | sort | tee alreadyPackages.txt
		;;

	"compare") # Packete suchen die auf Source installiert sind, aber nicht auf Target
		diff alreadyPackages.txt directPackages.txt | grep '>' | sed 's/^> //' | tee missingOnTarget.txt
		;;

	"explain") # Für jedes Packet die einzeilige Beschreibung suchen
		rm -f missingExplaination.txt
		for package in $(cat missingOnTarget.txt); do
			description="$(apt-cache show $package 2>/dev/null | sed -n '/^Description-de:/{s/^Description-de: //;p}' | head -1)";
			if [[ "$description" == "" ]]; then
				description="$(apt-cache show $package 2>/dev/null | sed -n '/^Description-en:/{s/^Description-en: //;p}' | head -1)";
			fi;
			if [[ "$description" == "" ]]; then
				description="$(apt-cache show $package 2>&1 1>/dev/null)";
			fi;
			if [[ "$description" == "" ]]; then
				description='-';
			fi;
			printf "%25s :\t%s\n" $package "$description" | tee -a missingExplaination.txt
		done
		;;

	"install") # Aus dem Explainpacket eine Liste zu installierender Packete erstellen
		echo $(sed -r 's/ *([^ ]*) :.*$/\1/' missingExplaination.txt)
		;;

	*)
		echo '$0 (source|target|compare|explain|install)'
		;;
esac
