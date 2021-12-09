#!/usr/bin/zsh

tempfile=$(/bin/tempfile)
tempfile2=$(/bin/tempfile)

wget -q -O - https://opendata.ecdc.europa.eu/covid19/casedistribution/csv > $tempfile

(
	for country in DEU SWE USA GRC CHN ITA ESP
	do
		cat $tempfile |\
		rg $country |\
		tac - |\
		awk '
		BEGIN { FS = ","; A2 = 0; A3 = 0; A4 = 0; A5 = 0; A6 = 0 }
		{ A7 = A6; A6 = A5; A5 = A4; A4 = A3; A3 = A2; A2 = A1; A1 = $5;
		sum = A7 + A6 + A5 + A4 + A3 + A2 + A1;
		nipw = sum / ( $10 / 100000 );
		printf "%s, '"$country"', %3.0f\n", $1, nipw }' |\
		sed -r 's%^(..)/(..)/(....)%\3-\2-\1%'
	done
) |\
rg -v '^2019' |\
rg -v '^2020-0[123]' |\
sort |\
sed 'N;N;N;N;N;N;s/\n/, /g;s/, 20..-..-..//g' > $tempfile2

today=$(date +%d/%m/%Y)
# head -10 "$tempfile2"

gnuplot -p -e "
set title 'Neuinfektionen der letzten sieben Tage pro 100.000 Einwohner';
set key left top;
set xdata time;
set xrange [ '01/04/2020':'$today' ];
set format x '%d.%m.%Y';
set timefmt '%Y-%m-%d';
plot '$tempfile2' using 1:3 title 'China' with lines,
	 '$tempfile2' using 1:5 title 'Germany' with lines,
	 '$tempfile2' using 1:7 title 'Spain' with lines,
	 '$tempfile2' using 1:9 title 'Greece' with lines,
	 '$tempfile2' using 1:11 title 'Italy' with lines,
	 '$tempfile2' using 1:13 title 'Sweden' with lines,
	 '$tempfile2' using 1:15 title 'USA' with lines;"

rm $tempfile $tempfile2
