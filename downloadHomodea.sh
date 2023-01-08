#!/bin/bash
# set -e

BEARER=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIyODI2ZWIwMC02NmJlLTExZWEtYjhlMC02ZmUzNzM3N2YyNmMiLCJ1bmFtZSI6bnVsbCwiZm4iOiJLIiwibG4iOiJXb2xrZW5zcHJpbmdlciIsImVtYWlsIjoiZmxvcmRlY2VyZXpvQHBvc3Rlby5kZSIsInRhZ3MiOlsiYnJvbnplIiwicGF5aW5nIiwidXNlciJdLCJhdXRoIjoicHdkIiwiZHQiOjE2NDE5MzQyNzA0ODQsImJvZHkiOm51bGwsImNsYWltcyI6e30sImlhdCI6MTY0MTkzNDI3MCwiZXhwIjoxNjQ0NTI2MjcwfQ.r7mksQGkW38NMSei85CX0JER8Te1XVkHa9O_dSiCwcg

links=$(cat <<EOT
https://app.homodea.com/kurs/aktive-meditation/aoM8
https://app.homodea.com/kurs/aktive-meditation/ct8X
https://app.homodea.com/kurs/aktive-meditation/fHXw
https://app.homodea.com/kurs/aktive-meditation/g0U1
https://app.homodea.com/kurs/aktive-meditation/jugv
https://app.homodea.com/kurs/aktive-meditation/M4HQ
https://app.homodea.com/kurs/aktive-meditation/PTta
https://app.homodea.com/kurs/aktive-meditation/QHBc
https://app.homodea.com/kurs/aktive-meditation/QjUb
https://app.homodea.com/kurs/aktive-meditation/ShM0
https://app.homodea.com/kurs/aktive-meditation/uIJg
https://app.homodea.com/kurs/aktive-meditation/uYXR
https://app.homodea.com/kurs/aktive-meditation/VKBF
https://app.homodea.com/kurs/aktive-meditation/vrkF
https://app.homodea.com/kurs/life-charger-daily/ahwD
https://app.homodea.com/kurs/life-charger-daily/eDU0
https://app.homodea.com/kurs/life-charger-daily/EGvA
https://app.homodea.com/kurs/life-charger-daily/IBj2
https://app.homodea.com/kurs/life-charger-daily/IHkF
https://app.homodea.com/kurs/life-charger-daily/OIQ8
https://app.homodea.com/kurs/life-charger-daily/Qtha
https://app.homodea.com/kurs/life-charger-daily/QuK1
https://app.homodea.com/kurs/life-charger-daily/rRzI
https://app.homodea.com/kurs/life-charger-daily/sSOS
https://app.homodea.com/kurs/life-charger-daily/Tz5f
https://app.homodea.com/kurs/life-charger-daily/wdA1
https://app.homodea.com/kurs/life-charger-daily/XyTL
https://app.homodea.com/kurs/lifebooster-finde-deine-antwort/CoNM
EOT
)

for kurs in $links
do
    chapter=$(echo $kurs | cut -d'/' -f5)
    id=$(echo $kurs | cut -d'/' -f6)
    # echo https://api.homodea.com/api/v1/courses/$chapter/lessons/$id
    json=$(http https://api.homodea.com/api/v1/courses/$chapter/lessons/$id "authorization:Bearer $BEARER" |\
        jq -r .lessons_by_section.section.name,.lesson.player.url_mp3 | tr '\n' ';')
    savename=$(echo $json | cut -d';' -f1 | sed 's/[0-9][0-9] | //;s/Aktive Meditation | //;s/ | /, /g;s/ *$/.mp3/;')
    # echo $id $savename; continue
    filename=$(echo $json | cut -d';' -f2 | cut -d'/' -f4)
    # echo "$filename -> $savename"
    touch "Veit Lindau - ${savename:0:-4} -> $chapter:$id.notice"
    http --output "Veit Lindau - ${savename:0:-4}.json" https://api.homodea.com/api/v1/courses/$chapter/lessons/$id "authorization:Bearer $BEARER"
    http --output "Veit Lindau - ${savename}" --download https://files.homodea.com/private/videos/$filename
done
