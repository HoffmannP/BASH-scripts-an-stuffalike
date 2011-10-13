#!/bin/bash

URL=('https://mail1-thueringen.dfn.de:83/Search?h=5e5b6ca358329a5f025afa14d7f191db&email=p2lebe%40uni-jena.de' 'https://mail2-thueringen.dfn.de:83/Search?h=95043ab93c3c9b7f71b3db50ceb05ed3&email=p2lebe%40uni-jena.d'e);

function releaseMails {
	URL="$1";
    referer="${URL%/*}"'/';
    request="$referer"'/Dispatcher';
    userAgent='User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30';
    cfile="$(tempfile)";
    formData[0]='action="Message:Release"';
    formData[1]='screen="Search"';
    formData[2]='page=""';
    formData[3]='ignore_escapes%3Acriterion=""';
    formData[4]='pg=""';
    formData[5]='pageSize="25"';
    formData[6]='message_action1=""';
    formData[7]='toggle_msg="mid[]"';
    formData[8]='message_action2="Release"';
	fields="$(\
        wget -q -O - --no-check-certificate --user-agent="$userAgent" --save-cookies "$cfile" "$URL" | \
        grep '^    <input class="" type="checkbox"' | \
        sed -r 's/.*value="([0-9]{8})".*/mid%5B%5D="\1"/'
    )";
    if [[ "$fields" == "" ]]; then
		echo "No mails to release";
		return;
    fi;
    formData="$(echo $fields | sed 's/ /\&/g')";
    exFile="$(tempfile)";
    cat "$cfile";
    echo wget -O "$exFile" --no-check-certificate --user-agent="$userAgent" --load-cookies "$cfile" --referer="$referer" --post-data="$formData" "$request"
    shred "$cfile";
    rm "$cfile";
	echo $exFile;
}

for ((i=0; i<${#URL[*]}; i++)); do
	releaseMails ${URL[i]}
done

