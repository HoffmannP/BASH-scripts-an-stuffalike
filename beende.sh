#!/usr/bin/zsh

kinder=(leander linus laurin)
 name=$1
 if [[ $kinder[(Ie)$name] -eq 0 ]]
 then
     echo "Session for '$name' cannot be ended" >&2
 else
     echo "Ending session for '$name'"
     sudo -u $name killall -u $name
 fi
