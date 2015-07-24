from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from biom import load_table, Table
import json
import numpy as np
import requests
import tempfile
import agr
from agr.schema import (database_exists, database_connectivity,
                        schema_is_sane)


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
            fp.write(block)

    return tmp_name


def generate_per_sample_biom(biom_file, limit):
    """Yield (sample, biom_file)

    sample : the sample ID
    biom_file : a biom file in BIOM-format v1.0.0 of the sample
    limit : limit the number of per-sample biom files produced
    """
    table = load_table(biom_file)
    obs_ids = table.ids(axis='observation')
    obs_md = table.metadata(axis='observation')

    if limit is None:
        limit = np.inf

    count = 0
    for v, sample, _ in table.iter():
        if count >= limit:
            break

        single_sample = Table(v[:, np.newaxis], obs_ids, [sample], obs_md)
        single_sample.filter(lambda v_, i, md: v_ > 0, axis='observation')
        biomv1 = single_sample.to_json('AG')
        yield (sample, biomv1)
        count += 1


def insert_biom_sample(cur, id_, data):
    cur.execute("""insert into biom (sample, biom)
                   values (%s, %s)""", [id_, data])


def biom_unchanged(cur):
    """Check if the database has the same commit"""
    sha = json.loads(requests.get(agr.ag_biom_src_api).content)[0]['sha']
    cur.execute("select exists (select biom_sha from state where biom_sha=%s)",
                [sha])
    return cur.fetchone()[0]


def update_biom_sha(cur):
    """Update the database biom MD5 in use"""
    sha = json.loads(requests.get(agr.ag_biom_src_api).content)[0]['sha']
    cur.execute("insert into state (biom_sha) values (%s)", [sha])


if __name__ == '__main__':
    import sys

    if not database_connectivity():
        sys.stderr.write("Cannot connect to the database")
        sys.exit(1)
    if not database_exists():
        sys.stderr.write('Database does not exist')
        sys.exit(1)
    if not schema_is_sane():
        sys.stderr.write('Schema does not appear to be sane')
        sys.exit(1)

    c = connect(user=agr.db_user, host=agr.db_host, password=agr.db_password,
                dbname=agr.db_name)
    c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = c.cursor()

    if biom_unchanged(cur):
        # data are the same, no change
        sys.exit(0)

    biom_file = downloader(agr.ag_biom_src, True)

    limit = 10 if agr.test_environment else None
    for sample_id, sample_biom in generate_per_sample_biom(biom_file, limit):
        insert_biom_sample(cur, sample_id, sample_biom)

    update_biom_sha(cur)
