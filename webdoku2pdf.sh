#!/bin/bash

echo checking prerequisits
sphinx=$(which "sphinx-build");
if [[ ! "$sphinx" ]]; then
    echo "Can't find »sphinx-build« binary!" >&2;
    exit 1;
fi
latex=$(which "pdflatex");
if [[ ! "$latex" ]]; then
    echo "Can't find »pdflatex« binary!" >&2;
    exit 2;
fi
wget=$(which "wget");
if [[ ! "$wget" ]]; then
    echo "Can't find »wget« binary!" >&2;
    exit 3;
fi
sed=$(which "sed");
if [[ ! "$sed" ]]; then
    echo "Can't find »sed« binary!" >&2;
    exit 4;
fi

echo analyzing index link
new="$1";
if [[ "$new" == "-r" ]]; then
    shift;
else
    new="";
fi;
del="$1";
if [[ "$del" == "-d" ]]; then
    shift;
else
    del="";
fi;
index="index"
download="$1";
path="$(dirname $download)";
suffix="$(basename $download)";
suffix=${suffix:${#index}};

if [[ ! "$2" ]]; then
    read -p "Name of project: " projname
else
    projname="$2";
fi
if [[ ! "$3" ]]; then
    read -p "Version of $projname: " projversion
else
    projversion="$3";
fi
echo creating config file
year=$(date +%Y);
wget -q --no-check-certificate https://github.com/fabpot/sphinx-php/raw/master/configurationblock.py
echo "import sys, os
sys.path.append(os.path.abspath('.'))
extensions = ['configurationblock']
master_doc = 'index'
project = u'$projname'
copyright = u'$year, $projname Team'
version = '$projversion'
release = '$projversion'
exclude_trees = ['_build']
pygments_style = 'sphinx'
latex_documents = [
('index', 'index.tex', u'$projname Documentation',
u'$projname Team', 'manual'),
]
latex_show_pagerefs = 1
latex_show_urls = 1
latex_papersize = {'papersize': 'a4paper'}

" > conf.py;

if [[ "$new" ]]; then
    echo "only reloading, no getting";
else
    echo "getting index file";
    index="index.rst";
    $wget -q -O $index "$1";

    dirs="";
    echo -n "getting all documentation files ";
    for name in $($sed -n $index -e '/^\.\. toctree/{:beg; n; s/^$//; T beg; :rep; n; s/^$//; t end; p; T rep; :end}'); do
    dir=$(dirname "$name");
    if [[ "$dir" ]]; then
       mkdir -p "$dir";
       dirs="$dirs $dir";
    fi;
    $wget -q -O "${name}.rst" "$path/$name$suffix";
    echo -n ".";
    done;
    echo "";
fi;

echo converting into latex document
index="index.tex";
$sphinx -b latex . . 1>/dev/null || exit 5;
tmpfile=$(tempfile);
cp $index $tmpfile;
cat $tmpfile | sed 's/ﬁ/fi/' > $index;
rm $tmpfile;

echo -n "creating latex 1/2";
$latex -halt-on-error $index 1>/dev/null || exit 6;

echo -e "\b\b\b2/2";
$latex -halt-on-error $index 1>/dev/null || exit 7;
mv index.pdf "${projname}_${projversion}.pdf"

echo cleaning up
rm conf*.{py,pyc}
rm index.{aux,tex,log,out,toc}
rm Makefile
rm *.{cls,sty,idx}
rm python.ist
rm -rf .doctrees
if [[ ! "$del" ]]; then
    rm -rf$dirs
    rm index.rst
fi;