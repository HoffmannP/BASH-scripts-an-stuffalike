#!/bin/bash
 
# Downloads latest Organizationally Unique Identifier (OUI) list from
# ieee.org in format suitable for use in nmap-mac-prefixes file.
 
err_exit()
{
 echo -e 1>&2
 exit 1
}
 
src="/usr/share/nmap/nmap-mac-prefixes"
 
UpdateNotice()
{
 cat << EOF
 
 Processing complete.
 
 Updated file saved as '$(pwd)/nmap-mac-prefixes'. It contains $missing OUI
 entries missing from the original ($src).
 
 You should manually review the updated version, if satisfied,
 replace the original ($src).
 
 Here are line counts from the original and updated versions:
 
EOF
}
 
LineCounts()
{
 wc -l $src $(pwd)/nmap-mac-prefixes | sed '/total$/d'
}
 
if ! [ -f $src ]; then
  echo "ERROR: required source file '$src' not found, I quit."
fi
 
if ! [ -x "$(type -P combine)" ]; then
  echo "Error: looks like 'combine' is not available"
  echo "Get it with e.g. 'apt-get install moreutils'"
  exit 1
fi
 
cd /tmp || err_exit 
 
for f in nmap-mac-prefixes oui.txt; do
  if [ -f $f ]; then
    rm $f || err_exit
  fi
done
 
cp $src . || err_exit
 
# get latest OUI file
echo "$(date +%F\ %T) $(basename $0): INFO: downloading oui.txt"
echo
wget http://standards.ieee.org/regauth/oui/oui.txt
 
if ! [ -f "oui.txt" ]; then
  echo "$(date +%F\ %T) $(basename $0): ERROR: oui.txt is missing"
  exit 1
fi
 
# save values from oui.txt in format used by nmap-mac-prefixes
echo "$(date +%F\ %T) $(basename $0): INFO: extracting values from oui.txt..."
grep "(base 16)" oui.txt | sed -r 's/( |\t)+/ /g;s/\(base 16\) //;s/^ //;' > nmap-oui
 
# if Org value is empty, set it to "Private"
echo "$(date +%F\ %T) $(basename $0): INFO: replacing empty Org with 'Private'..."
awk '{if ($2=="") $2="Private"; print}' nmap-oui > nmap-oui.tmp
mv nmap-oui.tmp nmap-oui
 
# extract just the OUI for comparison
echo "$(date +%F\ %T) $(basename $0): INFO: generating files for comparison..."
awk '{print$1}' nmap-oui > nmap-oui.id
awk '$1!="#" {print$1}' nmap-mac-prefixes > nmap-mac-prefixes.id
 
# generate a list of OUI present in oui.txt but missing in nmap-mac-prefixes
combine nmap-oui.id not nmap-mac-prefixes.id > missing.id
 
missing=$(cat missing.id | wc -l)
 
if [ "$missing" -eq 0 ]; then
  echo
  echo "Your local nmap-mac-prefixes is up to date, nothing to do."
else
  echo -e "\n# Appended from http://standards.ieee.org/regauth/oui/oui.txt" >> nmap-mac-prefixes
  sed -i '/^$/d' nmap-mac-prefixes
  # Append missing OUI to nmap-mac-prefixes
  echo "$(date +%F\ %T) $(basename $0): INFO: appending missing OUI to '$(pwd)/nmap-mac-prefixes'..."
  while read id; do
    grep $id nmap-oui >> nmap-mac-prefixes
  done < missing.id
  UpdateNotice
  LineCounts
fi
 
# cleanup
for f in oui.txt nmap-oui nmap-oui.id nmap-mac-prefixes.id missing.id; do
  if [ -f $f ]; then
    rm $f
  fi
done
