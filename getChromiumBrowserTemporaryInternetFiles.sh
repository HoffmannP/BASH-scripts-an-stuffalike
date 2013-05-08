
user=$(whoami)
chromepids=$(pgrep -u $user -f /usr/lib/chromium-browser/chromium-browser | tr -s ' ' "\t" | cut -f2 | tr [:cntrl:] ,)0

(for line in $(lsof -a -p $chromepids -u $user | egrep '\W+/var/tmp/' | tr -s ' ' "\t" | cut -f4- | egrep '^[0-9]+u\W+' | cut -f 1,6 | tr "\t" ':'); do
	fd=$(echo $line | sed -r 's/^([0-9]*).*$/\1/')
	name=$(basename $(echo $line | cut -d: -f2))
	path=$(ls -l /proc/*/fd/$fd | grep ' -> /var/tmp/'"$name"' (deleted)$' | cut -d ' ' -f9)
	echo $(file -L $path)
done) | column -s: -t