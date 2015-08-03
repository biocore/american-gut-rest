#!/usr/bin/env python
r"""A helpber script to populate a local test database

It is expected that 'ag.biom' is in the cwd
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from agr.schema import create_database
from agr.check_and_load import generate_per_sample_biom, insert_biom_sample

create_database()

c = connect(user='postgres', host='localhost', database='ag_rest')
c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = c.cursor()

it = generate_per_sample_biom('ag.biom', limit=10)
for sample_id, biomv1, biomtxt in it:
    insert_biom_sample(cur, sample_id, biomv1, biomtxt)
