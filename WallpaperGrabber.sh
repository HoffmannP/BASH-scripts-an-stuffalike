#!/bin/bash

# Aufrufmöglichkeit auf der Shell
# for i in `seq 1 10`; do ./WallpaperGrabber.sh; sleep 1; done

# Ich speichere die letzte Aufrufnummer am Ende des Skripts
counter=$(tail -1 "$0");
# Mein default user agent für wget
user_agent="Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Ubuntu/10.10 Chromium/10.0.648.133 Chrome/10.0.648.133 Safari/534.16";
 
# da nicht jede Nummer einem Hintergrundbild entspricht wird
# solange gesucht bis eine Nummber gefunden wird die passt
while [[ ! "$page_name" ]]; do
  counter=$[$counter+1];
  base_url="http://interfacelift.com/wallpaper/details/"$counter"/"
  forward=$(wget -q -O - $base_url | sed -n '/URL=/{s%^.*\(http://.*\.html\).*$%\1%;p}');
  page_name=$(echo $forward | sed 's%^.*/\(.*\)\.html.*$%\1%;s/_//;');
done;
 
# die beste 16:10 Auflösung raussuchen
resolution=$(wget -q -O - -U "$user_agent" $forward | sed -n '/16:10/{n;s%^.*>\([0-9]*x[0-9]*\)<.*$%\1%;p}');
page_id=$(printf %05d $counter);
image_url="http://interfacelift.com/wallpaper/7yz4ma1/"$page_id"_"$page_name"_"$resolution".jpg";

# Bild runterladen
img_path=$PWD/$page_id"_"$page_name"_"$resolution".jpg";
wget -q -U "$user_agent" -O $img_path --referer=$forward $image_url;

# neuen Coutner im Skript setzen
tmp_filename=$(tempfile);
(head -n -2 "$0"; echo; echo $counter) > $tmp_filename;
cat $tmp_filename > "$0";
rm $tmp_filename;

# Prüfe ob das Bild gültig ist (größer als 50kb)
# falls nicht starte das script neu
scriptpath=$PWD/$(basename $0);
cmp=$(du $img_path | awk '{print $1}');

if [ $cmp -lt 50 ]; then
 rm $img_path;
 exec $scriptpath;
fi
exit 0;

#Counter

0