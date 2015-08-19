#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os
import sys
import agr


def get_base():
    """Get the base support file configuration directory"""
    cwd = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    supp_files = '../agr/support_files'
    return os.path.join(cwd, supp_files)


def get_server_template():
    """Source the nginx server template"""
    conf_template = os.path.join(get_base(), 'server_config.template')
    with open(os.path.join(conf_template)) as fp:
        return fp.read()


def get_http_template():
    """Source the nginx http template"""
    conf_template = os.path.join(get_base(), 'http_config.template')
    with open(os.path.join(conf_template)) as fp:
        return fp.read()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage = "usage: %s [http|server]\n" % sys.argv[0]
        sys.stderr.write(usage)
        sys.exit(1)

    if sys.argv[1] == 'http':
        template = get_http_template()
        populated = template % {'base_conf_dir': agr.base_conf_dir,
                                'db_user': agr.db_user,
                                'db_name': agr.db_name,
                                'db_password': agr.db_password,
                                'db_host': agr.db_host}
        filename = os.path.join(agr.base_conf_dir, 'nginx.conf')
    elif sys.argv[1] == 'server':
        template = get_server_template()
        print template
        populated = template % {'serverport': agr.serverport,
                                'location_base': agr.location_base}
        filename = os.path.join(agr.base_conf_dir, 'agr.apiserver.conf')
    else:
        sys.stderr.write("Unknown argument: %s\n" % sys.argv[1])
        exit(1)

    if os.path.exists(filename):
        sys.stderr.write("%s already exists\n" % filename)
        sys.exit(1)

    with open(filename, 'w') as fp:
        fp.write(populated)
