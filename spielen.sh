#!/bin/bash

TIME=${1:-35}
USER=linus
EASYPASS=$USER
PASS=Linus1Linus

echo -en "$EASYPASS\n$EASYPASS\n" | sudo passwd $USER
while true
do
    test $(who | grep $USER | wc -l) -gt 0 && break
done
date
echo -en "$PASS\n$PASS\n" | sudo passwd $USER
echo "killall -u $USER" | sudo at -m now + $TIME min
