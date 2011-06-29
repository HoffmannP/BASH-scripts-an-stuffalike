#!/bin/bash

echo $0;

Port=3306;
# server.csv is a file containing in the first column your servers name (for your eyes) and the servers address (for your computer)
SF="bin/server.csv";

running=$(ps auxf | grep "$Port:localhost:$Port" | grep -v grep | tr -s '[:blank:]' '\t' | cut -f 2)
if [[ "$running" ]]; then
	zenity --question --text="Eine andere Instanz dieses Programms läuft bereits. Soll diese abgrebochen werden? (ansonsten wird diese Aktion abgebrochen)";
	if [[ $? == 0 ]]; then
		kill $running;
	else
		echo "still running" >&2;
		exit 5;
	fi;
fi;

active=$(netstat -tan 2>/dev/null | grep ":$Port" | wc -l);
if [[ $active > 0 ]]; then
	PID="$(netstat -ptan 2>/dev/null | grep -m 1 ":$Port" | tr -s '[:blank:]*' '\t' | cut -f 7)";
	if [[ "$PID" == "-" ]]; then
		zenity --error --text="Der Port $Port ist bereits durch anderes Programm belegt welches nicht beendet werden kann. Die Aktion wird abgebrochen!";
		echo "port is busy (not killable by user)" >&2;
		exit 1;
	fi;
	
	zenity --question --text="Der Port $Port ist bereits durch anderes Programm belegt [$PID]. Soll dieses Programm beendet werden? (ansonsten wird die Aktion abgebrochen)";
	if [[ $? == 1 ]]; then
		echo "port is busy (don't want to kill)" >&2;
		exit 2;
	fi;

	kill $(echo $PID | cut -d '/' -f 1);
	active=$(netstat -tan 2>/dev/null | grep ":$Port" | wc -l);
	if [[ $active > 0 ]]; then
		zenitry --error --text="Das Programm $PID konnte nicht beendet werden. Die Aktion wird abgebrochen!";
		echo "port is busy (could not kill)" >&2;
		exit 3;
	fi;
fi;

Server=$(zenity --list --text "Server wählen" --radiolist --column="✓" --column="Server" $(for S in $(cut -d, -f1 "$SF"); do echo "0 $S "; done));

if [[ "$Server" == "" ]]; then
	echo "No server selected" >&2;
	exit 4;
fi;

host=$(grep "^$Server," "$SF" | cut -d, -f2)
 
echo "ssh -c blowfish -NL $Port:localhost:$Port $host &"
ssh -c blowfish -NL $Port:localhost:$Port $host
