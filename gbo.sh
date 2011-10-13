#!/bin/bash

userAgent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30";

clear;

for url in $(wget -q -O - http://feeds2.feedburner.com/gbo-zitate | \
	grep '<link>http://feedproxy' | \
	sed -r 's/.*\/([0-9]*)<\/link>/http:\/\/german-bash.org\/\1/')
do
	wget -q -O - --user-agent="$userAgent" --referer="http://german-bash.org/335228" "$url" | \
		sed -nr '
/^ *<span class="quote_zeile">/{
  :begin
  s/^ *<span class="quote_zeile">(.*)<\/span>.*/\1/;
  t print
  N
  s/[\r\n]//g
  b begin
  :print
  p
}'      | \
	    recode utf8..latin9 | \
	    recode html..utf8;
	echo;
done;

