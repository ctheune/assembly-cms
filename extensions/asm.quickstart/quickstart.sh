#!/bin/bash
echo "Assembly CMS quickstart installer"
echo
echo "Fetching and building Assembly CMS ..."

hg -q clone http://bitbucket.org/ctheune/assembly-cms
cd assembly-cms
cat > buildout.cfg <<EOF
[buildout]
extends = profiles/base.cfg

[app]
admin-password = admin
EOF

python2.5 bootstrap.py
bin/buildout -q

./etc/init.d/asm.cms-zeo start > /dev/null
./etc/init.d/asm.cms-server start > /dev/null

echo "Server is running at http://localhost:8081."
echo "The initial username is 'admin' and the password is 'admin'."
