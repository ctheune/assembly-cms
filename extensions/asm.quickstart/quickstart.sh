#!/bin/bash
set -e

echo "Assembly CMS quickstart installer"
echo
echo "Installing Assembly CMS. This can take a few minutes."
echo
echo "Fetching code ..."
hg -q clone http://bitbucket.org/ctheune/assembly-cms
cd assembly-cms
cat > buildout.cfg <<EOF
[buildout]
extends = profiles/base.cfg

[app]
admin-password = admin
EOF

echo "Bootstrapping ..."
python2.5 bootstrap.py > /dev/null

echo "Building ..."
bin/buildout -q > /dev/null 

./etc/init.d/asm.cms-zeo start > /dev/null
./etc/init.d/asm.cms-server start > /dev/null

echo "Done."
echo
echo "Server is running at http://localhost:8081."
echo "The initial username is 'admin' and the password is 'admin'."
echo 
echo "You can stop the server and database by executing these commands:"
echo "./etc/init.d/asm.cms-server stop"
echo "./etc/init.d/asm.cms-zeo stop"
