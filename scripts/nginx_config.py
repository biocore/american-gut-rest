#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os
import agr


def get_nginx_template():
    cwd = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    supp_files = '../agr/support_files'
    conf_template = os.path.join(cwd, supp_files, 'nginx_config.template')
    with open(os.path.join(conf_template)) as fp:
        return fp.read()


if __name__ == '__main__':
    template = get_nginx_template()

    print template % {'db_user': agr.db_user,
                      'db_name': agr.db_name,
                      'db_password': agr.db_password,
                      'db_host': agr.db_host}
