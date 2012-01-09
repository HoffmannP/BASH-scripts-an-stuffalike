#!/bin/bash

# Aufrufmöglichkeit auf der Shell
# for i in `seq 1 10`; do ./$0.sh; sleep 1; done
# Als Argument kann die Auflösung (z.B. 4:3 oder 16:9 angegeben werden)
# Zudem kann "-d" als Option angegeben werden um das Wallpaper nur ins Arbeitsverzeichnis zu speichern

download="";

if [[ "$1" == "-d" ]]; then
  download="-d";
  shift;
fi

# Meine Auflösung als erstes optionales Argument
if [[ "$1" != "" ]]; then
  resolution="$1";
  shift;
  if [[ "$1" == "-d" ]]; then
  	download="-d";
  	shift;
  fi	
else
  resolution="16:10";
fi

# Ich speichere die letzte Aufrufnummer am Ende des Skripts
counter=$(tail -1 "$0");

# Mein default user agent für wget
user_agent="Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Ubuntu/10.10 Chromium/10.0.648.133 Chrome/10.0.648.133 Safari/534.16";
# gnome2 speichert den Desktophintergrund in diesem "registry" key
gconf_key="/desktop/gnome/background/picture_filename"
# Minimale Bilddateigröße in kByte
minsize=50;

# da nicht jede Nummer einem Hintergrundbild entspricht wird
# solange gesucht bis eine Nummber gefunden wird die passt
while [[ ! "$page_name" ]]; do
  counter=$[$counter+1];
  base_url="http://interfacelift.com/wallpaper/details/"$counter"/"
  forward=$(wget -q -O - $base_url | sed -n '/URL=/{s%^.*\(http://.*\.html\).*$%\1%;p}');
  page_name=$(echo $forward | sed 's%^.*/\(.*\)\.html.*$%\1%;s/_//;');
done;

# die beste $resolution Auflösung raussuchen
resol=$(wget -q -O - -U "$user_agent" $forward | sed -n '/'"$resolution"'/{n;s%^.*>\([0-9]*x[0-9]*\)<.*$%\1%;p}');
page_id=$(printf %05d $counter);
image_url="http://interfacelift.com/wallpaper/7yz4ma1/"$page_id"_"$page_name"_"$resol".jpg";

# Bild runterladen
img_path=$(tempfile);
wget -q -U "$user_agent" -O $img_path --referer=$forward $image_url;

# neuen Counter im Skript setzen
tmp_filename=$(tempfile);
(head -n -2 "$0"; echo; echo $counter) > $tmp_filename;
cat $tmp_filename > "$0";
rm $tmp_filename;

# Prüfe ob das Bild gültig ist (größer als $minsize)
# falls nicht starte das script neu
if [[ $(du $img_path | cut -f1) -lt $minsize ]]; then
	rm $img_path;
	$(which $0) $download $resolution
	exit 0;
fi;

if [[ $download == "-d" ]]; then
	mv $img_path "${PWD}/${page_id}_${page_name}_${resolution}_${resol}.jpg";
else
	gconftool-2 -s "$gconf_key" --type "string" $img_path
fi;

exit 0;

#Counter

285
