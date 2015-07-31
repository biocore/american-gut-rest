from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from biom import load_table, Table
import numpy as np
from agr.schema import create_database

create_database()

c = connect(user='postgres', host='localhost', database='ag_rest')
c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = c.cursor()

table = load_table('ag.biom')
obs_ids = table.ids(axis='observation')
obs_md = table.metadata(axis='observation')
it = table.iter()
for count in range(10):
    v, sample, md = it.next()
    single_sample = Table(v[:, np.newaxis], obs_ids, [sample], obs_md)
    single_sample.filter(lambda v, i, md: v > 0, axis='observation')
    biomv1 = single_sample.to_json('AG')
    cur.execute("""insert into biom (sample, biom)
                   values (%s, %s)""", [sample, biomv1])
