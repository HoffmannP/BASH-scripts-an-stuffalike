#!/bin/bash

eMail="p2lebe@uni-jena.de"
host="destroy-club.de"
user="web386"
pass='`$/XQr@sK(J`'

IP=$(tail -1 $0)
IP=${IP:2}

nIP=$(wget -q -O - "http://whatismyip.org")

if [[ "$IP" != "$nIP" ]]; then
	# echo "New IP: $nIP" | mail -s "$nIP" $eMail
    index=$(tempfile)
	echo '<html>
  <head><title>IP Address</title></head>
  <body><h1>'"$nIP"'</h1></body>
</html>' > $index;
	HOST=
	ftp -i -n $host <<EOF
user ${user} ${pass}
binary
cd /html
put ${index} index.html
quit
EOF
	(head -n-1 $0; echo -n "# "$nIP) > $index
	cat $index > $0
fi

# 188.103.236.80