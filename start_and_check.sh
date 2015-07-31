#!/bin/sh

# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

python agr/schema.py
python agr/check_and_load.py

psql -d ag_rest -c "select count(1) from biom"

if [ $? -ne 0 ]; then
    echo "Doesn't look like the test database is in place" >&2
fi

/usr/local/openresty/nginx/sbin/nginx -p `pwd`/ -c nginx.conf -s stop 
/usr/local/openresty/nginx/sbin/nginx -p `pwd`/ -c nginx.conf
curl -v http://127.0.0.1:8080/

if [ $? -ne 0 ]; then
    echo "Doesn't look like curl can connect to nginx" >&2
fi
