# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from biom import load_table, Table
import json
import re
import numpy as np
import requests
import tempfile
import agr
from agr.schema import (database_exists, database_connectivity,
                        schema_is_sane)


def downloader(url, binary):
    """Download a file

    Parameters
    ----------
    url : str
        The url to retrieve
    binary : bool
        Whether the file to download is binary

    Returns
    -------
    str
        The path to the downloaded file
    """
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
    """Generate per-sample BIOM files

    Parameters
    ----------
    biom_file : str
        A filepath to a BIOM table
    limit : int or None
        Limit the number of tables to load

    Returns
    -------
    str
        The sample ID
    str
        The table in BIOM Format v1.0
    str
        The table in the classic OTU table format
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
        biomtxt = single_sample.to_tsv(
            header_key='taxonomy',
            header_value='taxonomy',
            metadata_formatter=lambda x: '; '.join(x))
        yield (sample, biomv1, biomtxt)
        count += 1


def insert_biom_sample(cur, id_, biomv1, biomtxt):
    """Insert per-sample tables

    Parameters
    ----------
    cur : cursor
        A cursor to the database
    id_ : str
        A sample ID
    biomv1 : str
        A table in BIOM Format v1.0
    biomtxt : str
        A table in the classic OTU table format
    """
    cur.execute("""delete from biom where sample=%s""", [id_])
    cur.execute("""insert into biom (sample, biom, biomtxt)
                   values (%s, %s, %s)""", [id_, biomv1, biomtxt])


def insert_fastq_sample(cur, id_, data):
    """Insert a fastq download URL

    Parameters
    ----------
    cur : cursor
        A cursor to the database
    id_ : str
        A sample ID
    data : str
        The URL

    Notes
    -----
    It is possible that the accession map has more samples than the BIOM table
    if, for instance, a sample didn't yield sufficient sequence to be included
    in processing. This situation will also be encountered during testing.
    """
    cur.execute("select exists (select sample from biom where sample=%s)",
                [id_])

    if cur.fetchone()[0]:
        cur.execute("""delete from fastq where sample=%s""", [id_])
        cur.execute("""insert into fastq (sample, url)
                       values (%s, %s)""", [id_, data])


def biom_unchanged(cur):
    """Check if the database has the same commit

    Parameters
    ----------
    cur : cursor
        A cursor to the database
    """
    sha = json.loads(requests.get(agr.ag_biom_src_api).content)[0]['sha']
    cur.execute("select exists (select biom_sha from state where biom_sha=%s)",
                [sha])
    return cur.fetchone()[0]


def update_biom_sha(cur):
    """Update the database biom MD5 in use

    Parameters
    ----------
    cur : cursor
        A cursor to the database
    """
    sha = json.loads(requests.get(agr.ag_biom_src_api).content)[0]['sha']
    cur.execute("insert into state (biom_sha) values (%s)", [sha])


def do_biom_update(cur):
    """Perform the BIOM table update

    Parameters
    ----------
    cur : cursor
        A cursor to the database
    """
    biom_file = downloader(agr.ag_biom_src, True)

    limit = 10 if agr.test_environment else None
    it = generate_per_sample_biom(biom_file, limit)
    for sample_id, biomv1, biomtxt in it:
        insert_biom_sample(cur, sample_id, biomv1, biomtxt)

    update_biom_sha(cur)


def do_fq_update(cur):
    """Perform the fastq data update

    Parameters
    ----------
    cur : cursor
        A cursor to the database

    Notes
    -----
    This step is not limited for the test environment as the data volume and
    compute is small.

    Much of this function is sourced from the American Gut repository.
    """
    ebi_url = "http://www.ebi.ac.uk/ena/data/warehouse/" \
              "filereport?accession=%(accession)s&result=read_run&" \
              "fields=secondary_sample_accession,submitted_ftp"
    fq_to_sample_id = re.compile('seqs_.*\.fastq\.gz$')

    # grab the accession -> sample map
    with open(downloader(agr.ag_accession_src, False)) as acc_fp:
        accession_map = json.loads(acc_fp.read())

    accessions = set(accession_map)

    for accession in accessions:
        resp = requests.get(ebi_url % {'accession': accession})

        if not resp.status_code == 200:
            raise requests.HTTPError("Unable to grab %s." % accession)

        for line in resp.content.splitlines()[1:]:
            if 'ERA371447' in line:
                # Corrupt sequence files were uploaded to EBI for one of the AG
                # rounds. Ignoring entries associated with this accession works
                # around the corruption
                continue

            parts = line.strip().split('\t', 1)
            if len(parts) != 2:
                # an oddity that occurs...
                continue
            else:
                fq_url = "ftp://%s" % parts[1]

            try:
                filename = fq_to_sample_id.search(fq_url).group(0)
            except:
                continue

            sample_id = filename.rstrip('.fastq.gz').strip('seqs_')
            insert_fastq_sample(cur, sample_id, fq_url)


if __name__ == '__main__':
    import sys

    if not database_connectivity():
        sys.stderr.write("Cannot connect to the database\n")
        sys.exit(1)
    if not database_exists():
        sys.stderr.write('Database does not exist\n')
        sys.exit(1)
    if not schema_is_sane():
        sys.stderr.write('Schema does not appear to be sane\n')
        sys.exit(1)

    c = connect(user=agr.db_user, host=agr.db_host, password=agr.db_password,
                dbname=agr.db_name)
    c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = c.cursor()

    if biom_unchanged(cur):
        # data are the same, no change
        sys.exit(0)

    do_biom_update(cur)
    do_fq_update(cur)
