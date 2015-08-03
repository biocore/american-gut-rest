# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os
import functools
from ConfigParser import ConfigParser

# configuration defaults
_defaults = {
    'db_user': 'postgres',
    'db_host': 'localhost',
    'db_password': '',
    'db_name': 'ag_rest',
    'test_environment': True,
    'ag_biom_src': 'https://github.com/biocore/American-Gut/blob/master/data/AG/AG_100nt_even10k.biom?raw=true',  # noqa
    'ag_biom_src_api': 'https://api.github.com/repos/biocore/American-Gut/commits?path=data/AG/AG.biom',  # noqa
    'ag_accession_src': 'https://github.com/biocore/American-Gut/blob/master/data/AG/accession_to_sample.json?raw=true'  # noqa
}


# source the config from a file or from _defaults
_config = ConfigParser()
if 'AGREST_CONFIG' in os.environ:
    with open(os.environ['AGREST_CONFIG']) as conf_fp:
        _config.readfp(conf_fp)
    get = functools.partial(_config.get, 'main')
    getboolean = functools.partial(_config.get, 'main')
else:
    def _get(item):
        return _defaults[item]
    get = _get
    getboolean = get


# set the configuration variables
db_user = get('db_user')
db_host = get('db_host')
db_password = get('db_password')
db_name = get('db_name')
test_environment = getboolean('test_environment')
ag_biom_src = get('ag_biom_src')
ag_biom_src_api = get('ag_biom_src_api')
ag_accession_src = get('ag_accession_src')


__all__ = ['db_user', 'db_hostname', 'db_password', 'db_name',
           'test_environment', 'ag_biom_src', 'ag_biom_src_api',
           'ag_accession_src']
