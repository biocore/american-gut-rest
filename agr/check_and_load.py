from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from biom import load_table, Table
from biom.util import safe_md5
import numpy as np
import requests
import tempfile


def downloader(url, binary):
    # derived from http://stackoverflow.com/a/14114741/19741
    mode = 'wb' if binary else 'w'
    tmp_name = None
    with tempfile.NamedTemporaryFile(mode, delete=False) as fp:
        tmp_name = fp.name
        response = requests.get(url, stream=True)

        if not response.ok:
            raise ValueError("Unable to download file")

        for block in response.iter_content(1024):
            handle.write(block)

    return tmp_name


c = connect(user='postgres', host='localhost', database='ag_rest')
c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = c.cursor()
cur.execute("""create table per_sample_biom
               (sample varchar,
                biom json,
                constraint pk_per_sample_biom primary key (sample))""")

table = load_table('ag.biom')
obs_ids = table.ids(axis='observation')
obs_md = table.metadata(axis='observation')
it = table.iter()
for count in range(10):
    v, sample, md = it.next()
    single_sample = Table(v[:, np.newaxis], obs_ids, [sample], obs_md)
    single_sample.filter(lambda v, i, md: v > 0, axis='observation')
    biomv1 = single_sample.to_json('AG')
    cur.execute("""insert into per_sample_biom (sample, biom)
                   values (%s, %s)""", [sample, biomv1])
