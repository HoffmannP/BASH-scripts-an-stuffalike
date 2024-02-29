#!/bin/bash

set -e

TMP_FILE="/tmp/Briefmarke.pbm"
COUNT=$[ ${2:-1} - 1 ]

X_OFFSET=$[ 150 + ( ( $COUNT % 2 ) * 904 ) ]
Y_OFFSET=$[ 325 + ( ( $COUNT / 2 ) * -99 ) ]

if [[ $COUNT -gt 1 ]]
then
	echo "Vielfaches muss noch geprüft werden" >&2
	exit 1
fi

convert -density 255 \
	-depth 8 \
	$1 \
	-background white \
	-flatten \
	-crop "710x384+${X_OFFSET}+${Y_OFFSET}" \
	-rotate 90 \
	$TMP_FILE

if [[ "$DEBUG" ]]
then
	kitty +kitten icat $TMP_FILE
	exit 0
fi

(
	# https://github.com/NaitLee/Cat-Printer.git
	cd /home/ber/Code/Cat-Printer
	python3 printer.py $TMP_FILE
)
rm $TMP_FILE
