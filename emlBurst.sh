#!/bin/bash

# TODO: Unicode-Handling von Mailbody und Dateinamen

mail="$1"

boundary=$(rg -i ^Content-Type: "$mail" | head -1 | cut -d= -f2 | tr -d '"\r')
files=$(csplit --prefix=.attachments "$mail" "/^--$boundary/" '{*}' | wc -l)
if [[ $files -lt 2 ]]
then
    echo "Could not split $mail" >&2
    exit 1
fi

bodyfile="${mail:0:-3}txt"
boundary=$(rg -i ^Content-Type: .attachments01 | head -1 | cut -d= -f2 | tr -d '"\r')
if [[ -n "$boundary" ]]
then
    text=$(csplit --prefix=.mailtext .attachments01 "/^--$boundary/" '{*}' | wc -l)
    cat $(rg -li '^Content-Type:.*text/plain' .mailtext*) |\
        awk 'BEGIN{ head=1 }{ if (head == 0) { print $0 } else { if (length($0) < 2) { head=0 } } }' |\
        sed 's/\r$//' > "$bodyfile"
    rm .mailtext*
else
    mv .attachments01 "$bodyfile"
fi
echo "$bodyfile"

for ((file=2; file<$files; file++)) {
    attachment=$(printf ".attachments%02d" $file)
    filename=$(cat $attachment |\
        awk '{ if ($0 ~ /^Content\-Disposition:/) { while (substr($0, length($0) - 1, 1) == ";") { printf $0 |"tr -d \r"; getline } printf $0 | "tr -d \r" } }' |\
        awk 'BEGIN { FS="=" }{ print $NF }' |\
        tr -d '"' | tr -d "'")
    if [[ -z "$filename" ]]
    then
        continue
    fi
    if [[ ${filename:0:9} == "-utf-8-B-" ]]
    then
        filename="$(echo ${filename:9:${#filename}-10} | base64 -d)"
    fi
    filename=$(basename "$filename") # only for security
    cat $attachment |\
        awk 'BEGIN{ head=1 }{ if (head == 0) { if (length($0) < 2) { head=1 } else { print $0 } } else { if (length($0) < 2) { head=0 } } }' |\
        sed 's/\r$//' | base64 -d > "$filename"
    echo "$filename"
}
rm .attachments*
