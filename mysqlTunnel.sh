#!/bin/bash

Port=3306

# server.csv is a file containing in the first column your servers name (for your eyes) and the servers address (for your computer)
SF="bin/server.csv";

TEXT_KillMysqlf="Eine andere Instanz dieses Programms läuft bereits. Soll diese beendet werden? (ansonsten wird diese Aktion abgebrochen)";
TEXT_Rootspace=" welches nur durch mit Rootrechten beendet werden kann";
TEXT_Userspace=" [%i]";
TEXT_KillElseone="Der Port %i ist bereits durch anderes Programm belegt %s. Soll dieses Programm beendet werden? (ansonsten wird diese Aktion abgebrochen)";
TEXT_KillMySQLd="Der Port %i ist bereits durch einen MySQL-Daemon belegt. Soll dieser beendet werden? (ansonsten wird diese Aktion abgebrochen)";
TEXT_KillFail="Das Programm %i konnte nicht beendet werden. Die Aktion wird abgebrochen!";
TEXT_Server="Server";
TEXT_ChooseServer="$TEXT_Server wählen";
TEXT_becomeRoot="Das port-blockierende Programm kann nur mit Rootrechten beendet werden";

running=$(ps auxf | grep "$Port:localhost:$Port" | grep -v grep | tr -s '[:blank:]' '\t' | cut -f 2)
if [[ "$running" ]]; then
	zenity --question --text="$TEXT_KillMysqlf";
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
	NAME="$(echo $PID | cut -d/ -f2)";
	if [[ $NAME == 'mysqld' ]]; then
		zenity --question --text="$(printf "$TEXT_KillMySQLd" $Port)";
		if [[ $? == 0 ]]; then
			mysqld stop;
		else
			echo "port is blocked [by mysqld] - don't want to unblock" >&2;
			exit 2;
		fi;
		break;
	else
		if [[ "$PID" == "-" ]]; then
			zenity --question --text="$(printf "$TEXT_KillElseone" $Port "$TEXT_Rootspace")";
			if [[ $? == 0 ]]; then
				PID="$(gksu -g --message "$TEXT_becomeRoot" netstat -ptan 2>/dev/null | grep -m 1 ":$Port" | tr -s \'[:blank:]*\' \'\t\' | cut -f 7)";
				NAME="$(echo $PID | cut -d/ -f2)";
				if [[ $NAME -eq 'mysqld' ]]; then
					gksu -g --message "$TEXT_becomeRoot" service mysql stop;
				else
					gksu -g --message "$TEXT_becomeRoot" kill $(echo $PID | cut -d/ -f1);
				fi
				active=$(netstat -tan 2>/dev/null | grep ":$Port" | wc -l);
				if [[ $active > 0 ]]; then
					zenitry --error --text="$(printf "$TEXT_KillFail" $PID)";
					echo "port is blocked - can\'t unblock" >&2;
					exit 3;
				fi;
				echo "port successfully unblocked by root";
			else
				echo "port is blocked - need to be root to unblock" >&2;
				exit 1;
			fi;
		else
			zenity --question --text="$(printf "$TEXT_KillElseone" $Port "$(printf $TEXT_Userspace $PID)")";
			if [[ $? == 0 ]]; then
				kill $(echo $PID | cut -d '/' -f 1);
				active=$(netstat -tan 2>/dev/null | grep ":$Port" | wc -l);
				if [[ $active > 0 ]]; then
					zenitry --error --text="$(printf $TEXT_KillFail $PID)";
					echo "port is blocked - can't unblock" >&2;
					exit 3;
				fi;
				echo "port successfully unblocked";
			else
				echo "port is blocked - don't want to unblock" >&2;
				exit 2;
			fi;
		fi;
	fi;
fi;

	Server=$(zenity --list --text "$TEXT_ChooseServer" --radiolist --column="✓" --column="$TEXT_Server" $(for S in $(cut -d, -f1 "$SF"); do echo "0 $S "; done));

	if [[ "$Server" == "" ]]; then
		echo "No server selected" >&2;
		exit 4;
	fi;

	host=$(grep "^$Server," "$SF" | cut -d, -f2)

	echo "ssh -c blowfish -NL $Port:localhost:$Port $host &";
	ssh -c blowfish -NL $Port:localhost:$Port $host
