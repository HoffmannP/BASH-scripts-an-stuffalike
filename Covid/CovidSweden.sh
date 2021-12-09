#!/usr/bin/zsh

if [[ -z "$1" ]]
then
	country=SWE
else
	country=$1
fi

tempfile=$(/bin/tempfile)

wget -q -O - https://opendata.ecdc.europa.eu/covid19/casedistribution/csv | rg $country > $tempfile

cat $tempfile |\
	tac - |\
	awk '
	BEGIN { FS = ","; A2 = 0; A3 = 0; A4 = 0; A5 = 0; A6 = 0 }
	{ A7 = A6; A6 = A5; A5 = A4; A4 = A3; A3 = A2; A2 = A1; A1 = $5;
	sum = A7 + A6 + A5 + A4 + A3 + A2 + A1;
	nipw = sum / ( $10 / 100000 );
	printf "%s [%3.0f]: ", $1, nipw;
	i=0; while (i++ < nipw && i < 51) { printf "." };
	while (nipw-- >= 50) { printf "#" };
	print "" }'

echo $country, $(cat $tempfile | head -1 | cut -d, -f7 | sed 's/_/ /g')

rm $tempfile
