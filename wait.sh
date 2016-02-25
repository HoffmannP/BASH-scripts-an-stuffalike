#!/bin/bash

waitFile="$HOME/.wait"

if [[ "$1" == "start" ]]; then
	rm "$waitFile"
	sleep 1s;
	touch "$waitFile"
else
	while [[ -e "$waitFile" ]]; do
		sleep 1s;
	done
fi;
