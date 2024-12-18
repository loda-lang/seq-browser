#!/usr/bin/env python3

import sys
import logging
import sqlite3


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


TEST_ENTRIES = [
    (37, 'Numbers that are not squares (or, the nonsquares).', 'easy,formula,loda,nice,nonn,pari', 'N. J. A. Sloane,Simon Plouffe,fzs600', ''),
    (96, 'a(n) = n*(n+3)/2.', 'easy,formula,loda,loda-formula,nice,nonn,pari', 'N. J. A. Sloane,Christian Krause', 'a(n) = binomial(n+2,2)-1'),
    (98, 'Number of partitions of n if there are two kinds of 1, two kinds of 2 and two kinds of 3.', 'easy,formula,loda,loda-loop,nonn', 'N. J. A. Sloane,UBT - Mikeejones', '')
]


def test_entry(dbconn, entry: tuple):
    logger.info('testing entry: {}'.format(entry[0]))
    query = 'SELECT * FROM seq_entries WHERE oeis_id = {};'.format(entry[0])
    dbcursor = dbconn.execute(query)
    row = dbcursor.fetchone()
    if row is None:
        logger.error('entry not found: {}'.format(entry[0]))
        exit(1)
    if row != entry:
        logger.error('entry mismatch:\nexpected: {}\n     got: {}'.format(entry, row))
        exit(1)


def test_database(dbconn):
    global TEST_ENTRIES
    for entry in TEST_ENTRIES:
        test_entry(dbconn, entry)


def print_sample(dbconn):
    query = 'SELECT * FROM seq_entries LIMIT 100;'
    dbcursor = dbconn.execute(query)
    for row in dbcursor:
        print(row)


def main():
    logger.info('testing database')
    try:
        dbconn = sqlite3.connect('seqs.sqlite3')
        # print_sample(dbconn)
        test_database(dbconn)
    except sqlite3.Error as error:
        logger.error('error while connecting to sqlite', error)
    finally:
        if dbconn:
            dbconn.close()


if __name__ == "__main__":
    main()
