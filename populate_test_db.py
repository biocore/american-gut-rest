from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

c = connect(user='postgres', host='localhost')
cur = c.cursor()
c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur.execute('drop database if exists ag_rest')
cur.execute('create database ag_rest')
cur.close()
c.close()

c = connect(user='postgres', host='localhost', database='ag_rest')
cur = c.cursor()
cur.execute('create table foo (a varchar, b varchar)')
cur.close()
c.close()

