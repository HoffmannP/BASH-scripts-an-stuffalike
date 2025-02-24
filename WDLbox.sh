if [ $(id -u) -ne 0 ]; then
	echo "Need to be root";
	exit 2;
fi;

$maxFileSize = "10MiB";

function mount { # url, folder
	url=$1;
	shift 1; folder=$1;
	webDavFolder=$(connectToWebDav $url);
	dev=(activateLVM $(find $webDavFolder -type f))
	mount $dev $folder
}

function create { # url, size
	url=$1;
	shift 1; size=$1;
	webDavFolder=$(connect $url);
	files=$(createLVMfiles $webDavFolder $size);
	vg=$(createVolumeGroup $files)
	lv=$(createPartition $vg)
	rollback $vg $lv
	deconnectFromWebDav $webDavFolder
}

function grow { # folder/url, +size
	folder=$1
	shift 1; size=$1;
	if [ ! -d $folder ]; then
		url=$folder;
		folder=$(connectToWebDav $url);
	fi;
	files=$(createLVMfiles $webDavFolder $size)
	expandLogicalVolume $file;		
	done;
	if [ $url ]; then
		deconnectFromWebDav $folder;
	fi;
}

function deconnect { # folder
	folder=$1
	umount $folder
	vg=$(vgdisplay -c | grep WLDbox | cut -d: -f1 | tr -d ' ');
	rollback $vg $lv
	deconnectFromWebDav $folder;
}

#################################################################################################
## Y O U   S H O U L D   N O T   C H A N G E   A N Y T H I N G   B E L O W   T H I S   L I N E ##
#################################################################################################


block="1MiB";
cylinder=2048;
prefix="WLDbox_LVM_file."

function nextFileName { # folder
	folder=$1
	lastFile=$(ls $folder -v $prefix* | tail -1);
	suffix=${lastFile[${#prefix}+1,${#lastFile}]};
	echo $suffix
	newSuffix=$[suffix+1];
	newFile="$folder/$prefix$newSuffix"
	echo $newFile
}

function connectToWebDav { # url
	url=$1;
	folder=$(mktemp --tempdir "/dev" "webDavLVM.XXXXXXXXXX");
	mount -t davfs "$url" "$folder";
	echo $folder;
}

function deconnectFromWebDav { # folder
	folder=$1;
	umount $folder;
}

function isLVMfile { # file
	file=$1
	file $file | egrep -o ' ID=0x8e, ' | wc -l
}

function realSize { # size
	size=$1;
	inBlocks=$(units $size"M" $block"M");
	if [ $(echo $inBlocks | grep '.' | wc -l) ]; then
		echo $[$(echo $inBlocks | cut -d. -f1)+1];
	else
		echo $inBlocks;
	fi;
}

function createLVMfile { # folder, size
	folder=$1;
	shift 1; size=$1;
	file=$(nextFileName $folder);
	dd if=/dev/zero of=$file bs=$block count=$count;
	echo 'u c x c '"$cylinder"' r n p 1   t 8e p w' | tr ' ' "\n" | fdisk $file;
	if [ ! $(isLVM $file) ]; then
		echo "File could not be created";
		exit 1
	fi;
	echo $file
}

function createLVMfiles { # folder, size
	folder=$1;
	shift 1; size=$1;
	maxFileSizeInBlocks=$(realSize $maxFileSize);
	lvmSizeInBlocks=$(realSize $size);
	files="";
	while [ $lvmSizeInBlocks -gt $maxFileSizeInBlocks ]; do
		files=$(createLVMfile $folder $maxFileSizeInBlocks)" files";
		lvmSizeInBlocks=$[$lvmSizeInBlocks - $maxFileSizeInBlocks];
	done
	files=$(createLVMfile $folder $lvmSizeInBlocks)" files";
	echo $files;
}

function addLVMfile { # vg, file
	vg=$1;
	shift 1; file=$1;
	loop=$(losetup -f --show $file)
	if [ $(vgck WLDbox 1>/dev/null 2>&1; echo $?) ]; then
		pvextend $vg $loop;
	else
		pvcreate -s $block $vg $loop;
	fi;
}

function createVolumeGroup { # file, file?, …
	vg="WDLbox.$RANDOM";
	while [ $# -gt 1 ]; do
		file=$1;
		addLVMfile $vg $file;
		shift 1;
	done;
	echo $vg;
}

function expandLogicalVolume { # file, file?, …
	vg=$(vgdisplay -c | grep WLDbox | cut -d: -f1 | tr -d ' ');
	while [ $# -gt 1 ]; do
		file=$1;
		addLVMfile $vg $file;
		shift 1;
	done;
	lv="LV_$vg";
	dev="/dev/WDLbox/$lv";
	lvextend -l100%VG $dev
	folder=$(mount | grep /dev/sda5 | cut -d' ' -f3)
	umound $dev;
	echo 'd 1 n p 1   p w' | tr ' ' "\n" | fdisk $dev
	mount $dev $folder;
}

function createPartition { # vg, ftype=ext3
	vg=$1;
	shift 1; folder=$1;
	shift 1 && ftype=$3 || ftype="ext3";
	lv="LV_$vg";
	dev="/dev/WDLbox/$lv";
	lvcreate -n $lv "WDLbox" -l100%VG $vg ;
	if [ $(fsck -t $ftype $dev 1>/dev/null 2>&1; echo $?) ]; then
		mkfs -t ext3 $dev;
	fi;
	echo $lv;
}

function rollback { # vg, lv=LV_${vg}
	vg=$1;
	shift 1 && lv=$1 || lv="LV_$vg";
	lvchange -an /dev/WLDbox/$lv;
	vgchange -an $vg;
	for device in $(pvdisplay -c | grep ':WLDbox:' | cut -d: -f1 | tr -d ' '); do
		losetup -d $device;
	done;
}

function activateLVM { # file, file?, …
	vg=$(vgdisplay -c | grep WLDbox | cut -d: -f1 | tr -d ' ');
	while [ $# -gt 1 ]; do
		file=$1;
		addLVMfile $vg $file;
		shift 1;
	done;
	lv="LV_$vg";
	echo $lv
	vgchange -ay $vg;
	lvchange -ay $lv;
	dev=$(vgdisplay -c | grep WLDbox | cut -d: -f1 | tr -d ' ')
	echo $dev;
}
