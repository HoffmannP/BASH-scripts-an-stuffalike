#!/bin/bash

duration=$(zenity --scale --text "Wie lange darf geschaut werden?" --value=30 --min-value=15 --max-value=60)

if [[ -z "$duration" ]]
then
    zenity --info --text="Abbruch"
	exit 0
else
    zenity --info --text="Noch $duration Minuten ab jetzt!"
fi

minus_five=$[ $duration - 5 ]
sleep "${minus_five}m"
zenity --info --text="Noch 5 Minuten" &
sleep 5s
pid=$(ps auxf | grep zenity | grep "Noch 5 Minuten" | tr -s ' ' "\t" | cut -f2)
kill $pid
sleep 5m

pid=$(ps auxf | egrep '^leli' | grep ck-launch-session | head -1 | tr -s ' ' "\t" | cut -f2)
kill $pid
