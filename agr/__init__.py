# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os
from ConfigParser import ConfigParser

# configuration defaults
_defaults = {
    # the server port is the port that the nginx webserver will listen on
    'serverport': '8080',

    # the base URL for the API. For instance, setting this to "/foo/bar" would
    # result in the nginx configuration location directives accepting requests
    # to endpoints stemming from that base such as "/foo/bar/otu"
    'location_base': '',

    # the base_conf_dir is the location for the nginx server config.
    # NOTE: there are multiple config files for nginx, the primary one being
    # the "http" config. The base_conf_dir houses other more specific configs
    # and in the case of american gut rest, it houses the specific "server"
    # config which includes details on the endpoints etc.
    'base_conf_dir': '.',

    # the db_* credentials are for READ access with the database
    'db_user': 'postgres',
    'db_host': 'localhost',
    'db_password': '',
    'db_name': 'ag_rest',

    # the admin_db_* credentials are for WRITE access with the database
    # NOTE: db_name and db_host are not replicated
    'admin_db_user': 'postgres',
    'admin_db_password': '',

    # Indicate if we're operating in a test_environment.
    # WARNING: if test_environment is True, then it is possible to drop the
    # database
    'test_environment': True,

    # ag_*_src configs are for the data sources themselves, these must be
    # URLs that can be retreived using requests.get
    'ag_biom_src': 'https://github.com/biocore/American-Gut/blob/master/data/AG/AG_100nt_even10k.biom?raw=true',  # noqa
    'ag_accession_src': 'https://github.com/biocore/American-Gut/blob/master/data/AG/accession_to_sample.json?raw=true',  # noqa

    # the ag_*api configs are for the specific RESTful interfaces pinged to
    # determine if there have been changes to the corresponding src files
    'ag_biom_src_api': 'https://api.github.com/repos/biocore/American-Gut/commits?path=data/AG/AG.biom'  # noqa
}


# source the config from a file or from _defaults
_config = ConfigParser()
if 'AGREST_CONFIG' in os.environ:
    with open(os.environ['AGREST_CONFIG']) as conf_fp:
        _config.readfp(conf_fp)

    def get(key):
        try:
            return _config.get('main', key).strip("'").strip('"')
        except:
            return _defaults[key]

else:
    def get(item):
        return _defaults[item]


# set the configuration variables
serverport = get('serverport')
location_base = get('location_base')
base_conf_dir = get('base_conf_dir')
db_user = get('db_user')
db_host = get('db_host')
db_password = get('db_password')
db_name = get('db_name')
admin_db_user = get('admin_db_user')
admin_db_password = get('admin_db_password')
test_environment = True if get('test_environment') == 'True' else False
ag_biom_src = get('ag_biom_src')
ag_biom_src_api = get('ag_biom_src_api')
ag_accession_src = get('ag_accession_src')


__all__ = ['serverport', 'db_user', 'db_hostname', 'db_password', 'db_name',
           'admin_db_user', 'admin_db_password', 'test_environment',
           'location_base', 'ag_biom_src', 'ag_biom_src_api',
           'ag_accession_src']
