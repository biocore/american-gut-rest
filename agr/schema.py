# ----------------------------------------------------------------------------
# Copyright (c) 2011-2015, The American Gut Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import agr


# table definitions, these are of the form: [(table_name, table_definition)].
# the motivation for this structure is to allow for checking if tables exist
# easily (see schema_is_sane)
tables = [
    ('biom',
        """create table biom (
           sample varchar,
           biom json,
           biomtxt text,
           constraint pk_biom primary key(sample)
           )"""),
    ('metadata',
        """create table metadata (
           sample varchar,
           category varchar,
           value varchar,
           constraint pk_metadata primary key (sample, category),
           constraint fk_metadata foreign key (sample) references biom(sample)
           )"""),
    ('fastq',
        """create table fastq (
        sample varchar,
        url varchar,
        constraint pk_fastq primary key (sample),
        constraint fk_fastq foreign key (sample) references biom(sample),
        constraint uc_fastq unique (url)
        )"""),
    ('state',
        """create table state (
           biom_sha varchar)""")
]


def database_connectivity(user=agr.db_user, password=agr.db_password,
                          host=agr.db_host):
    """Determine if we can connect to the database

    Paramters
    ---------
    user : str
        The database usermame
    password : str
        The password for the user
    host : str
        The database host

    Returns
    -------
    bool
        True if a connection was made, False otherwise
    """
    try:
        c = connect(user=user, password=password, host=host)
    except:
        return False
    else:
        c.close()
        return True


def database_exists(user=agr.db_user, password=agr.db_password,
                    host=agr.db_host, dbname=agr.db_name):
    """Determine if the database exists

    Paramters
    ---------
    user : str
        The database usermame
    password : str
        The password for the user
    host : str
        The database host
    dbname : str
        The name of the database to connect to

    Returns
    -------
    bool
        True if the database exists, False otherwise
    """
    try:
        c = connect(user=user, password=password, host=host, dbname=dbname)
    except:
        return False
    else:
        c.close()
        return True


def schema_is_sane():
    """Check to see if the expected tables exist

    Notes
    -----
    Assumes we have connectivity and the database exists.

    The structure of the tables is _not_ verified, only checks that the table
    names exist.

    Database credentials are sourced from the agr module (e.g., the environment
    configuration.

    Returns
    -------
    bool
        The expected tables appear to exist
    """
    c = connect(user=agr.db_user, password=agr.db_password,
                host=agr.db_host, dbname=agr.db_name)
    cur = c.cursor()

    for table_name, _ in tables:
        cur.execute("""select exists(select *
                                     from information_schema.tables
                                     where table_name=%s)""", [table_name])
        if not cur.fetchone()[0]:
            return False
    return True


def schema_has_data():
    """Check to see if the schema appears to have data

    Notes
    -----
    Assumes we have connectivity and the database exists.

    The structure of the tables is _not_ verified, only checks that there
    appears to be rows in the tables.

    Database credentials are sourced from the agr module (e.g., the environment
    configuration.

    Returns
    -------
    bool
        If all of the tables appear to have data.
    """
    if not schema_is_sane():
        return False

    c = connect(user=agr.db_user, password=agr.db_password,
                host=agr.db_host, dbname=agr.db_name)
    cur = c.cursor()

    for table_name, _ in tables:
        cur.execute("select count(1) from %s" % table_name)
        if cur.fetchone()[0] == 0:
            return False
    return True


def create_database():
    """Create the database and the schema

    Notes
    -----
    Assumes we have connectivity.

    Database credentials are sourced from the agr module (e.g., the environment
    configuration.
    """
    c = connect(user=agr.admin_db_user, password=agr.admin_db_password,
                host=agr.db_host)

    c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = c.cursor()
    cur.execute('drop database if exists ag_rest')
    cur.execute('create database %s' % agr.db_name)
    cur.close()
    c.close()

    c = connect(user=agr.admin_db_user, password=agr.admin_db_password,
                host=agr.db_host, dbname=agr.db_name)

    c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = c.cursor()

    for _, table in tables:
        cur.execute(table)


if __name__ == '__main__':
    import sys
    if not database_connectivity():
        sys.stderr.write("Cannot connect to the database\n")
        sys.exit(1)

    if not agr.test_environment:
        sys.stderr.write("This does not appear to be a test environment\n")
        sys.exit(1)

    if database_exists() and schema_is_sane() and schema_has_data():
        sys.exit(0)
    else:
        create_database()
