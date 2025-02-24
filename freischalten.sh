#!/bin/bash

if [[ "$1" == "+" ]]
then
    chmod o+x /usr/bin/firefox
    chmod o+x /usr/bin/google-chrome
    chmod o+x /usr/bin/minecraft-launcher
else
    chmod o-x /usr/bin/firefox
    chmod o-x /usr/bin/google-chrome
    chmod o-x /usr/bin/minecraft-launcher
fi