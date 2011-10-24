#!/bin/bash

ironPortUrlsFile="$(dirname $0)/ironPortUrls.csv";
i=0;
while read line; do
	let i=$[i+1];
	URL[$i]="$line";
done < "$ironPortUrlsFile";

function releaseMails {	
URL="$1";
    userAgent='User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30';
    cfile="$(tempfile)";
    formData[0]='action=Message%3ARelease';
    formData[1]='screen=Search';
    formData[2]='page'=;
    formData[3]='ignore_escapes%3Acriterion=';
    formData[4]='pg=';
    formData[5]='pageSize=25';
    formData[6]='message_action1=';
    formData[7]='toggle_msg=mid[]';
    formData[8]='message_action2=Release';
	fields="$(\
        wget -q -O - --no-check-certificate --user-agent="$userAgent" --save-cookies "$cfile" --keep-session-cookies "$URL" | \
        grep '^    <input class="" type="checkbox"' | \
        sed -r 's/.*value="([0-9]{8})".*/mid%5B%5D=\1/'
    )";
    if [[ "$fields" == "" ]]; then
		echo "No mails to release";
		return;
    fi;
    formData[9]="$(echo $fields| sed 's/ /\&/g')";
	formData="$(echo ${formData[*]} | sed 's/ /\&/g')";
    exFile="$(tempfile)";
    referer="$URL";
    request="${URL%/*}"'/Dispatcher'; 	
	wget -q \
		-O /dev/null \
		--no-check-certificate \
		--user-agent="$userAgent" \
		--load-cookies "$cfile" \
		--keep-session-cookies \
		--save-cookies "$cfile" \
		--referer="$referer" \
		--post-data="$formData" \
		"$request"
    shred -u "$cfile";
}


for ((i=1; i<${#URL[*]}; i++)); do
	releaseMails ${URL[i]}
done

