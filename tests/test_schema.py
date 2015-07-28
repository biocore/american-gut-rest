#!/usr/bin/env python

from unittest import TestCase, main

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import agr
from agr.schema import (database_connectivity, database_exists, schema_is_sane,
                        schema_has_data, create_database, tables)


if not agr.test_environment:
    import sys
    sys.stderr.write("This is not a test environment!\n")
    sys.exit(1)


def dropdb():
    c = connect(user=agr.db_user, password=agr.db_password, host=agr.db_host)
    cur = c.cursor()
    c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur.execute("drop database if exists %s" % agr.db_name)
    c.commit()
    cur.close()
    c.close()


def createdb():
    c = connect(user=agr.db_user, password=agr.db_password, host=agr.db_host)
    c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = c.cursor()
    cur.execute("create database %s" % agr.db_name)
    c.commit()
    cur.close()
    c.close()


def createtable(name):
    c = connect(user=agr.db_user, password=agr.db_password, host=agr.db_host,
                dbname=agr.db_name)
    cur = c.cursor()
    cur.execute("create table %s (foo varchar)" % name)
    c.commit()
    cur.close()
    c.close()


def insertfoo(name):
    c = connect(user=agr.db_user, password=agr.db_password, host=agr.db_host,
                dbname=agr.db_name)
    cur = c.cursor()
    cur.execute("insert into %s (foo) values ('bar')" % name)
    c.commit()
    cur.close()
    c.close()


class SchemaTests(TestCase):
    def test_database_connectivity(self):
        # assumes we actually can connect with the provided credentials
        self.assertTrue(database_connectivity())
        self.assertFalse(database_connectivity(user='foobarnotexists'))

    def test_database_exists(self):
        dropdb()
        self.assertFalse(database_exists())
        createdb()
        self.assertTrue(database_exists())

    def test_schema_is_sane(self):
        dropdb()
        createdb()
        self.assertFalse(schema_is_sane())
        createtable(tables[0][0])
        self.assertFalse(schema_is_sane())

        for tablename, _ in tables[1:]:
            createtable(tablename)

        self.assertTrue(schema_is_sane())

    def test_schema_has_data(self):
        dropdb()
        createdb()
        self.assertFalse(schema_has_data())

        for tablename, _ in tables:
            createtable(tablename)

        self.assertFalse(schema_has_data())
        insertfoo(tables[0][0])
        self.assertFalse(schema_has_data())

        for tablename, _ in tables[1:]:
            insertfoo(tablename)

        self.assertTrue(schema_has_data())

    def test_create_database(self):
        dropdb()
        create_database()
        self.assertTrue(database_connectivity())
        self.assertTrue(database_exists())
        self.assertTrue(schema_is_sane())
        self.assertFalse(schema_has_data())


if __name__ == '__main__':
    main()
