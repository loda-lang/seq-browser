#! /usr/bin/env python3

import os
import sys
import logging
import sqlite3
import subprocess
import concurrent.futures

sys.path.append('sidneycadot/oeis')
from sidneycadot.oeis.oeis_entry    import parse_oeis_entry
from sidneycadot.oeis.timer         import start_timer
from sidneycadot.oeis.exit_scope    import close_when_done
from sidneycadot.oeis.setup_logging import setup_logging
import sidneycadot.oeis.fetch_oeis_database as fetch_oeis_database


logger = logging.getLogger(__name__)

def create_database_schema(dbconn):
    schema = """
             CREATE TABLE IF NOT EXISTS seq_entries (
                 oeis_id               INTEGER  PRIMARY KEY NOT NULL,
                 name                  TEXT     NOT NULL,
                 keywords              TEXT     NOT NULL
             );
             """
    dbconn.execute(schema)


def process_oeis_entry(oeis_entry):
    (oeis_id, main_content, bfile_content) = oeis_entry
    parsed_entry = parse_oeis_entry(oeis_id, main_content, bfile_content)
    result = (
        parsed_entry.oeis_id,
        parsed_entry.name,
        ",".join(str(keyword) for keyword in parsed_entry.keywords)
    )
    return result


def process_database_entries(file_in, file_out):
    BATCH_SIZE = 1000
    with start_timer() as timer:
        with close_when_done(sqlite3.connect(file_in)) as dbconn_in, close_when_done(dbconn_in.cursor()) as dbcursor_in:
            with close_when_done(sqlite3.connect(file_out)) as dbconn_out, close_when_done(dbconn_out.cursor()) as dbcursor_out:
                create_database_schema(dbconn_out)
                with concurrent.futures.ProcessPoolExecutor() as pool:
                    dbcursor_in.execute("SELECT oeis_id, main_content, bfile_content FROM oeis_entries ORDER BY oeis_id;")
                    while True:
                        oeis_entries = dbcursor_in.fetchmany(BATCH_SIZE)
                        if len(oeis_entries) == 0:
                            break
                        logger.log(logging.PROGRESS, "Processing OEIS entries A{:06} to A{:06} ...".format(oeis_entries[0][0], oeis_entries[-1][0]))
                        query = "INSERT INTO seq_entries(oeis_id, name, keywords) VALUES (?, ?, ?);"
                        dbcursor_out.executemany(query, pool.map(process_oeis_entry, oeis_entries))
                        dbconn_out.commit()
        logger.info("Processed all database entries in {}.".format(timer.duration_string()))


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
    update_repo('https://github.com/loda-lang/loda-programs.git', '/tmp/loda-programs')
    update_repo('https://github.com/archmageirvine/joeis.git', '/tmp/joeis')
    os.makedirs('logfiles', exist_ok=True)
    fetch_oeis_database.main()
    with setup_logging('logfiles/oeis_parsed.log'):
        if os.path.exists('seqs.sqlite3'):
            os.remove('seqs.sqlite3')
        process_database_entries('oeis.sqlite3', 'seqs.sqlite3')


if __name__ == "__main__":
    main()
