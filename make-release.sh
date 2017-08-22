#!/bin/bash

PLUGNAME="TrayTip"
SRCFILE="$PLUGNAME/__init__.py"
sed -n -E \
    -e '1,/^eg\.RegisterPlugin/d' \
    -e '/^\)$/,$d' \
    -e 's/^ *//' \
    -e "s/ \"/ u'/" \
    -e "s/\",/'/" \
    -e '/^(name|author|version|url|guid|description)/p' \
    $SRCFILE > info.py
VERSION=`grep ^version info.py | cut -d\' -f2`

cat info.py

zip -r $PLUGNAME-$VERSION.egplugin info.py $PLUGNAME \
    -x '*.pyc' -x '.*.sw*'
