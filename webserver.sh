#!/bin/sh

directory=$(zenity  --file-selection --title="Serve from" --directory)

echo $directory

if [ -z "$directory" ]
then
	exit 1
fi

usedPorts=$(tempfile)
netstat -tan | tr -s ' ' "\t" | cut -f 4 | cut -d: -f2 | egrep '^....$' > $usedPorts

portlist=$(tempfile)
(
for A in 8 5 7 2 1 3 4 6 9
do
	for B in 0 8 5 7 2 1 3 4 6 9
	do
		echo $A$A$B$B
		echo $A$B$A$B
		echo $A$B$B$A
	done
done
) | sort -R > $portlist

port=$(grep -f $usedPorts -v $portlist | head -1)

name=$(pwgen -0A 20 1)

docker run -d --name $name -v "$directory":/var/www:ro -p $port:8080 trinitronx/python-simplehttpserver

rm $portlist $usedPorts

zenity --question \
	--text "Serving <b>$directory</b> under <a href='http://localhost:$port'>http://localhost:$port</a>" \
	--no-wrap --icon-name "network-server" ||\
	docker rm -f $name
