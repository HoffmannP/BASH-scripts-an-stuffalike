if [[ "$1" == "-h" ]]; then
  echo <<EOF
File to convert all entries from a Password Gorilla¹ Database into an KeePass importable KeePass(X)-XML file

Usage: $0 [-d DELIMITER] [-S] INFILE [OUTFILE]
  DELIMITER may only be none-unicode character
  -S changes default from KeePassX²-xml-format to standard KeePass 1.x-xml-format³
  INFILE may be an csv/txt-exportet file from Password Gorilla
  if OUTFILE is ommitted output will be print to screen only

  ¹) https://github.com/zdia/gorilla/wiki/
  ²) http://www.keepassx.org
  ³) http://keepass.info/help/base/importexport.html#xml
EOF
fi;

if [[ "$1" == "-d" ]]; then
  shift;
  d="$1";
  shift;
else
  d=",";
fi;

to=$(tempfile);
tp=$(tempfile);

if [[ "$1" == "-S" ]]; then
	shift;

    # Official and STANDARD XML-Fileformat with unique UUIDs (THIS IS NOT TESTED)
	sed 's/\x00//g;' "$1" | sed '/^'$d'/=' | sed '/^..$/{N; s/\(..\)\n/###\1/;}' > $tp;
	for i in $(sed -n '/^###/{s/###\([^'$d']*\)'$d'.*$/\1/;p}' $tp); do
		sed 's/###'$i'/'$(uuidgen)'/;' $tp > $to;
		mv $to $tp;
	done;
	(
		echo '<?xml version="1.0" encoding="UTF-8"?>';
		echo '<pwlist>';
		iconv -f latin1 $tp |\
        	sed '
      			s/\\\././g
      			s/&/\&amp;/g
      			s/</\&lt;/g
      			s/>/\&gt;/g
      			s/"/\&quot;/g
      			s/'"'"'/\&apos;/g
      		' |\
            awk -F "$d" '{print "<pwentry>\n\t<group tree=\"General\">"$2"</group>\n\t<title>"$3"</title>\n\t<username>"$4"</username>\n\t<url/>\n\t<password>"$5"</password>\n\t<notes>"$6"</notes>\n\t<uuid>"$1"</uuid>\n\t<image>0</image>\n\t<creationtime>2011-06-27T11:40:41</creationtime>\n\t<lastmodtime>2011-06-27T11:40:41</lastmodtime>\n\t<lastaccesstime>2011-06-27T11:40:41</lastaccesstime>\n\t<expiretime expires=\"false\">2999-12-28T23:59:59</expiretime>\n</pwentry>";}' |\
            sed '/      <notes>/{
            	s/      <notes>\(.*\)<\/notes>/\1/;
            	s/\\n/\n/g;
            	s/^[ \n\t]*//;
            	s/[ \n\t]*$//;
            	s/^/      <notes>/;
            	s/$/<\/notes>/;
            }'
        echo '</pwlist>';
	) > $to;

else

	# Inofficial KeePassX Version (tested and running)
	sed 's/\x00//g; s/\\\././g;' "$1" | iconv -f latin1 > $tp;
	(
		echo '<!DOCTYPE KEEPASSX_DATABASE>';
		echo '<database>';
		for i in $(cut -d "$d" -f2 $tp | sort -u | sed 's/ /::##::blank::##::/g;'); do
			group=$(echo $i | sed 's/::##::blank::##::/ /g;');
			echo '  <group>';
			echo '    <title>'$group'</title>';
			echo '    <icon>1</icon>';
			grep -F "$d$group$d" $tp |\
                sed '
                    s/\\\././g
                    s/&/\&amp;/g
                    s/</\&lt;/g
                    s/>/\&gt;/g
                    s/"/\&quot;/g
                    s/'"'"'/\&apos;/g
                ' |\
                awk -F "$d" '{print "    <entry>\n      <title>"$3"</title>\n      <username>"$4"</username>\n      <password>"$5"</password>\n      <url></url>\n      <comment>"$6"</comment>\n      <icon>1</icon>\n      <creation>2011-06-27T11:40:41</creation>\n      <lastaccess>2011-06-27T11:40:41</lastaccess>\n      <lastmod>2011-06-27T11:40:41</lastmod>\n      <expire>Nie</expire>\n    </entry>";}' |\
                sed '/      <comment>/{
                    s/      <comment>\(.*\)<\/comment>/\1/;
                    s/\\n/\n/g;
                    s/^[ \n\t]*//;
                    s/[ \n\t]*$//;
                    s/^/      <comment>/;
                    s/$/<\/comment>/;
                }'
			echo '  </group>';
		done;
		echo '</database>';
	) > $to;

fi;


shred -u $tp;
if [[ "$2" != "" ]]; then
  mv $to "$2";
else
  cat "$to";
  shred -u "$to";
fi;
