#! /usr/bin/env python3

import os
import sys
import logging
import sqlite3
import subprocess
import concurrent.futures

sys.path.append('sidneycadot/oeis')
import sidneycadot.oeis.fetch_oeis_database as fetch_oeis_database
from sidneycadot.oeis.setup_logging import setup_logging
from sidneycadot.oeis.exit_scope import close_when_done
from sidneycadot.oeis.timer import start_timer
from sidneycadot.oeis.oeis_entry import parse_oeis_entry


logger = logging.getLogger(__name__)

def create_database_schema(dbconn):
    schema = """
             CREATE TABLE IF NOT EXISTS seq_entries (
                 oeis_id               INTEGER  PRIMARY KEY NOT NULL,
                 name                  TEXT     NOT NULL,
                 keywords              TEXT     NOT NULL,
                 contributors          TEXT     NOT NULL
             );
             """
    dbconn.execute(schema)


def process_oeis_entry(oeis_entry):
    (oeis_id, main_content, bfile_content) = oeis_entry
    entry = parse_oeis_entry(oeis_id, main_content, bfile_content)
    keywords = entry.keywords
    contributors = []
    if entry.author and len(entry.author) > 0:
        contributors.append(entry.author.replace("_", ""))
    if entry.maple_programs and len(entry.maple_programs) > 0:
        keywords.append('maple')
    if entry.mathematica_programs and len(entry.mathematica_programs) > 0:
        keywords.append('mathematica')
    if entry.other_programs and entry.other_programs.find('(PARI)') >= 0:
        keywords.append('pari')
    prefix = int(entry.oeis_id/1000)
    java_path = '/tmp/joeis/src/irvine/oeis/a{:03}/A{:06}.java'.format(prefix, entry.oeis_id)
    if os.path.exists(java_path):
        keywords.append('java')
    loda_path = os.path.join(os.path.expanduser('~'), 'loda', 'programs', 'oeis', '{:03}'.format(prefix), 'A{:06}.asm'.format(entry.oeis_id))
    if os.path.exists(loda_path):
        keywords.append('loda')
        with open(loda_path) as loda_file:
            for line in loda_file:
                if line.startswith('; Submitted by '):
                    contributors.append(line[14:].strip())
    result = (
        entry.oeis_id,
        entry.name,
        ','.join(str(k) for k in keywords),
        ','.join(str(c) for c in contributors)
    )
    return result


def process_database_entries(file_in, file_out):
    BATCH_SIZE = 1000
    with start_timer() as timer:
        with close_when_done(sqlite3.connect(file_in)) as dbconn_in, close_when_done(dbconn_in.cursor()) as dbcursor_in:
            with close_when_done(sqlite3.connect(file_out)) as dbconn_out, close_when_done(dbconn_out.cursor()) as dbcursor_out:
                create_database_schema(dbconn_out)
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    dbcursor_in.execute(
                        "SELECT oeis_id, main_content, bfile_content FROM oeis_entries ORDER BY oeis_id;")
                    while True:
                        oeis_entries = dbcursor_in.fetchmany(BATCH_SIZE)
                        if len(oeis_entries) == 0:
                            break
                        logger.log(logging.PROGRESS, "Processing OEIS entries A{:06} to A{:06} ...".format(
                            oeis_entries[0][0], oeis_entries[-1][0]))
                        query = "INSERT INTO seq_entries(oeis_id, name, keywords, contributors) VALUES (?, ?, ?, ?);"
                        dbcursor_out.executemany(query, pool.map(
                            process_oeis_entry, oeis_entries))
                        dbconn_out.commit()
        logger.info("Processed all database entries in {}.".format(
            timer.duration_string()))


def update_repo(url, path):
    if not os.path.isdir(os.path.join(path, '.git')):
        p = subprocess.run(['git', 'clone', url, path])
        if p.returncode != 0:
            exit(1)
    else:
        p = subprocess.run(['git', 'pull'], cwd=path)
        if p.returncode != 0:
            exit(1)


def main():
    # update joeis
    update_repo('https://github.com/archmageirvine/joeis.git', '/tmp/joeis')

    # update loda
    loda_bin = os.path.join(os.path.expanduser('~'), 'loda', 'bin', 'loda')
    p = subprocess.run([loda_bin, 'update'])
    if p.returncode != 0:
        logger.error('error updating loda')
        exit(1)

    # update oeis
    os.makedirs('logfiles', exist_ok=True)
    fetch_oeis_database.main()

    # generate final database
    with setup_logging('logfiles/seqs_parsed.log'):
        if os.path.exists('seqs.sqlite3'):
            os.remove('seqs.sqlite3')
        process_database_entries('oeis.sqlite3', 'seqs.sqlite3')


if __name__ == "__main__":
    main()
