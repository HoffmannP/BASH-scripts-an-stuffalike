#!/bin/bash

mail="$1"

boundary=$(rg -i ^Content-Type: "$mail" | head -1 | cut -d= -f2 | tr -d '\r')
files=$(csplit --prefix=.attachments "$mail" "/^--$boundary/" '{*}' | wc -l)
if [[ $files -lt 2 ]]
then
    echo "Could not split $mail" >&2
    exit 1
fi

bodyfile="${mail:0:-3}txt"
boundary=$(rg -i ^Content-Type: .attachments01 | head -1 | cut -d= -f2 | tr -d '\r')
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

for ((file=2; file<$[files-1]; file++)) {
    attachment=$(printf ".attachments%02d" $file)
    filename=$(rg -i '^Content-Disposition:' $attachment | cut -d= -f2 | tr -d '"\r' | tr -d "'")
    # cat .attachments02 | awk '/Content-Disposition/{ line=$0; while (substr($0, length($0) - 1, 1) == ";") { getline; line=line$0 }; print line }'
    filename=$(basename "$filename") # only for security
    cat $attachment |\
        awk 'BEGIN{ head=1 }{ if (head == 0) { if (length($0) < 2) { head=1 } else { print $0 } } else { if (length($0) < 2) { head=0 } } }' |\
        sed 's/\r$//' | base64 -d > "$filename"
    echo "$filename"
}
# rm .attachments*
