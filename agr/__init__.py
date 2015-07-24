db_user = 'postgres'
db_host = 'localhost'
db_password = ''
db_name = 'ag_rest'
test_environment = True
ag_biom_src = 'https://github.com/biocore/American-Gut/blob/master/data/AG/AG_100nt_even10k.biom?raw=true'
ag_biom_src_api = 'https://api.github.com/repos/biocore/American-Gut/commits?path=data/AG/AG.biom'

__all__ = ['db_user', 'db_hostname', 'db_password', 'db_name',
           'test_environment', 'ag_biom_src', 'ag_biom_src_api']
