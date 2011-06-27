#!/bin/bash

# Ich speichere die letzte Aufrufnummer am Ende des Skripts
counter=$(tail -1 "$0");
# Mein default user agent für wget
user_agent="Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Ubuntu/10.10 Chromium/10.0.648.133 Chrome/10.0.648.133 Safari/534.16";
# gnome2 speichert den Desktophintergrund in diesem "registry" key
gconf_key="/desktop/gnome/background/picture_filename"

# da nicht jede Nummer einem Hintergrundbild entspricht wird
# solange gesucht bis eine Nummber gefunden wird die passt
while [[ ! "$page_name" ]]; do
  counter=$[$counter+1];
  base_url="http://interfacelift.com/wallpaper/details/"$counter"/"
  forward=$(wget -q -O - $base_url | sed -n '/URL=/{s%^.*\(http://.*\.html\).*$%\1%;p}');
  page_name=$(echo $forward | sed 's%^.*/\(.*\)\.html.*$%\1%;s/_//;');
done;

die beste 4:3 Auflösung raussuchen
resolution=$(wget -q -O - -U "$user_agent" $forward | sed -n '/4:3/{n;s%^.*>\([0-9]*x[0-9]*\)<.*$%\1%;p}');
page_id=$(printf %05d $counter);
image_url="http://interfacelift.com/wallpaper/7yz4ma1/"$page_id"_"$page_name"_"$resolution".jpg";

# Bild mit temporärem Dateinamen als Hintergrundbild setzen
tmp_filename=$(tempfile);
wget -q -U "$user_agent" -O $tmp_filename --referer=$forward $image_url;
gconftool-2 -s "$gconf_key" --type "string" $tmp_filename

# neuen Coutner im Skript setzen
tmp_filename=$(tempfile);
(head -n -2 "$0"; echo; echo $counter) > $tmp_filename;
cat $tmp_filename > "$0";
rm $tmp_filename;
exit 0;

#Counter

0