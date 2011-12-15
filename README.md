# Descriptions

(of the different BASH-Scripts in this repository)

## No liability what so ever ##

### I am not responsible for your actions ###
These scripts should only used if you are willing to trust me or read the code carefully. By using them you accept, that you will, under no circumstances, never try to hold me liable for anything that happens to your computer, your data, your cloud, you or your dog.
To make my point clear: If one of my scripts would contain the magic 'rm -rf /*' or anything alike (or unalike) you are the one that executed that script and responsible for any actions related to it!

### Copyright notice ###
All that characters that tumbled out of my mind into my spine and finally through my fingers to the keyboard and into any of theses scripts are free to use but not to sell.
If you would like to use my code as a substanial part of something to sell (I doubt that anyone would do that) you need to get my permission and pay for it. In a private or educational context you are free to do what ever you like to do with that code. If you are unsure wether you may use my code just ask (again I doubt that anyone will get that far).

### Status ###
My scripts are working (or worked) for me. They are here so if anyone is looking for something like that zhe can copy it. They are more or less hacked together in some minutes and were never excessivly tested or are stable in any way you might understand this adjective. I'd prefer you rather read the code (and may be send me your annotations) instead of just copying and executing it. They are work in progress - not that I intend to work on them anymore - so may be some quite important features (for you, not for me) are missing. Feel free to add them (and be kind and send your changes back to me).

## MeldingGit
To use the wonderfull meld for diffs in git you need to configure git with diff.external set to this script (meld4git.sh).

## Password Database Converter ##
The 'convertGorilla2KeePass.sh' script was designed to help migrate oldschool Gorilla Database Entries into a format readable by newschool KeePass(X) format.
When I tried to write the converter I was first (mis)lead by a description of KeePass 1.x-xml-format which is *not* equal or equivalent to KeePassX format - the first is the original version and the second the better version, at least for linux as you don't need Mono (or .NET).
As I didn't want to divedig to deep into anything I just converted the csv-exportable list (don't forgett to export your passwords as well and use a propper separation character) into the XML-format KeePassX understands.
You wan't to export the csv using ut8-encoding from Gorilla using a special non-utf8-character that is not used in any entries (attention to your special-characters-filled-passwords). Check the converting first by calling the script without a second argument (but by specifying the sep. character using -d Option). You will see the converted xml. To save it into a file use pipe or a second (file-)argument.
Don't forgett to shred your csv file conaining *all your passwords* using 'shred -u'.

## MySQL Tunnel ##
This script 'mysqlTunnel.sh' checks if port 3305 is already taken. If yes it tries to kill that program or otherwise fails. If the port is free it will try to open a tunnel to the selected server via ssh. It reads available servers from a csv-server file. That's it.

## Wallpaper ##
Have a boring wallpaper as good as it may be? Change it on a regular basis. The 'wallpaper.sh' script gets a new wallpaper from one of that big wallpaper sites. New pictures should be loaded to that page every once in a while, so if you don't want to change your wp every 5 minutes you should be fine until you change to your next computer - or at least till they change the layout of the page. Just execute it. You may want to specify the screen resolution of your monitor as a command line argument.
New (and improved): You can specify "-d" command line switch to only download the next wallpaper in line into the current folder (so you may use it for something else.

## webdoku2pdf.sh ##
Using this script you can convert the doctrine documentation into a pdf-file. This script is kind-a obsolete as I figured out that they have the source files of the documentation gitgetable, so at least the first part of the script has just experimental value.

## Xdebug_geben_tunnel.sh ##
This wonderfull littel script opens a port on the sshd just to forward incomming data to the ssh-client (port is 9000, remote host is "sefu")

## IronTrop.sh ##
Automatically forwards (frees) all quarantined mails from ironPort, just write all your magic URL codes into the csv-file.

## gbo.sh ##
Grabs the newest german-BASH.org quotes

## playlist.py ##
My first-try python script that fetches the recent songs aired on the "Antenne Thüringen"-programm (a local radio station in Thueringia, Germany located in Erfurt). I don't want to listen to their program but desperatly want to know whats going on in the world of popular music. So I sometime in the future will write another script that figures out who's on the hot rotation.
Beside that I 1) learned how to parse extremly buggy HTML-code using a XML-DOM-parser and 2) how to write python at all (not knee deep but at least my first real experience). I must say I like python!
Feel free to use this parser for other radio stations (it's prepared for that)  but let me know, it might help me to figure out who's hot right now.