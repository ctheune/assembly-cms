#!/bin/sh

for prog in curl gcc make tar gzip bzip2; do
    if test -z "`which $prog`"; then
        echo "$prog is needed!"
        exit 1
    fi
done

cp buildout.cfg.example buildout.cfg || exit 1

PYTHON_VERSION="2.5.4"

APP_ROOT="`pwd`"
PACKAGES_ROOT="$APP_ROOT"/packages
PYTHON_ROOT="$APP_ROOT"/python

PYTHON_PACKAGE="http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.bz2"

# Install Python
mkdir -p "$PACKAGES_ROOT"
cd "$PACKAGES_ROOT"
curl -s "$PYTHON_PACKAGE" | tar xvj
cd Python-"${PYTHON_VERSION}"/
./configure --prefix="$PYTHON_ROOT"
make
make install

# Clean up installation packages
cd "$APP_ROOT"
rm -rf "$PACKAGES_ROOT"

# Bootstrap this application
"$PYTHON_ROOT"/bin/python bootstrap.py

# Compile this application
cd "$APP_ROOT"
"$APP_ROOT"/bin/buildout
