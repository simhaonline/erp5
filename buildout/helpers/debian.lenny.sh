#!/bin/sh

PACKAGE_LIST="""\
automake1.9
bison
build-essential
cpio
flex
gcc
gettext
libboost-dev
libboost-program-options-dev
libboost-regex-dev
libboost-serialization-dev
libbz2-dev
libgc-dev
libgdbm-dev
libgif-dev
libglib2.0-dev
libjpeg62-dev
libldap2-dev
libncurses5-dev
libneon27-gnutls-dev
libpng12-dev
libreadline-dev
librsync-dev
libsasl2-dev
libsdl-gfx1.2-dev
libsdl-image1.2-dev
libsdl1.2-dev
libssl-dev
libsvn-dev
libtool
libxml2-dev
libxslt1-dev
make
openssl
patch
python-setuptools
rpm
subversion
subversion-tools
tesseract-ocr-dev
xvfb
zip
zlib1g-dev\
"""

apt-get install $PACKAGE_LIST $@
