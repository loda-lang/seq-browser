#!/usr/bin/env python3

import os
import sys
import logging
import sqlite3
import subprocess


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def update_loda() -> str:
    logger.info('updating loda')
    loda_home = os.path.join(os.path.expanduser('~'), 'loda')
    loda_programs_path = os.path.join(loda_home, 'programs')
    loda_bin = os.path.join(loda_home, 'bin', 'loda')
    p = subprocess.run([loda_bin, 'update'])
    if p.returncode != 0:
        logger.error('error updating loda')
        exit(1)
    return loda_programs_path


def load_stats() -> tuple:
    logger.info('loading stats')
    loda_home = os.path.join(os.path.expanduser('~'), 'loda')
    programs_csv = os.path.join(loda_home, 'stats', 'programs.csv')
    inceval_programs = set()
    logeval_programs = set()
    with open(programs_csv) as file:
        for line in file:
            entries = line.split(',')
            if entries[0].isnumeric():
                id = int(entries[0])
                if int(entries[3]) == 1:
                    inceval_programs.add(id)
                if int(entries[4]) == 1:
                    logeval_programs.add(id)
    return (inceval_programs, logeval_programs)


def fetch_list(name : str, min_size = 350000) -> list:
    loda_api_base_url = 'http://api.loda-lang.org'
    url = "{}/miner/v1/oeis/{}.gz".format(loda_api_base_url, name)
    logger.info('fetching {} list'.format(name))
    cmd = "curl -sO {} && gunzip -f {}.gz".format(url, name)
    p = subprocess.run(cmd, shell=True)
    if p.returncode != 0:
        logger.error('error fetching {}'.format(name))
        exit(1)
    result = [None] * min_size
    oeis_id = 0
    content = None
    with open(name, 'r') as file:
        for line in file:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            if line[0] != 'A':
                logger.error('error parsing {}'.format(line))
                exit(1)     
            current_id = int(line[1:7])
            current_content = line[8:].strip()       
            if current_id != oeis_id:
                while oeis_id >= len(result) :
                    result.append(None)
                result[oeis_id] = content
                oeis_id = current_id
                content = current_content
            else:
                content = content + '\n' + current_content
    if oeis_id != 0 and len(content) > 0:
        while oeis_id >= len(result) :
            result.append(None)
        result[oeis_id] = content
    return result


def load_program(oeis_id: int, loda_programs_path: str) -> str:
    folder = '{:03}'.format(int(oeis_id/1000))
    file_name = 'A{:06}.asm'.format(oeis_id)
    loda_path = os.path.join(loda_programs_path, 'oeis', folder, file_name)
    if not os.path.exists(loda_path):
        return None
    with open(loda_path) as loda_file:
        return loda_file.readlines()


def extract_details(names: list, authors: list, comments: list, formulas: list, keywords: list, programs: list, 
                    inceval_programs: set, logeval_programs: set, loda_programs_path: str):
    contributors = [None] * len(names)
    new_keywords = [None] * len(names)
    loda_formulas = [None] * len(names)
    num_loda_programs = 0
    num_loda_formulas = 0
    for i in range(len(names)):
        if i % 1000 == 0:
            logger.info('extracting details for entries {}-{}'.format(i, i+999))
        keys = keywords[i].split(',') if keywords[i] else []
        if formulas[i]:
            keys.append('formula')
        desc = names[i] if names[i] else ''
        if comments[i]:
            desc += ' ' + comments[i]
        desc = desc.lower().replace('\n', ' ')
        if 'conjecture' in desc or 'it appears' in desc or 'empirical' in desc:
            keys.append('conjecture')
        if 'decimal expansion' in desc:
            keys.append('decimal-expansion')
        if ' e.g.f.' in desc:
            keys.append('egf-expansion')
        if ' g.f.' in desc:
            keys.append('gf-expansion')
        if programs[i] and programs[i].find('(PARI)') >= 0:
            keys.append('pari')
        conts = []
        if authors[i]:
            author = authors[i].split(',')[0].strip().replace('_', '')
            if author:
                conts.append(author)
        program = load_program(i, loda_programs_path)
        if program:
            num_loda_programs += 1
            keys.append('loda')
            for line in program:
                if line.startswith('; Submitted by '):
                    conts.append(line[14:].strip())
                if line.startswith('; Formula:'):
                    keys.append('loda-formula')
                    loda_formulas[i] = line[10:].strip()
                    num_loda_formulas += 1
                if line.strip().startswith('lpb'):
                    keys.append('loda-loop')
        if i in inceval_programs:
            keys.append('loda-inceval')
        if i in logeval_programs:
            keys.append('loda-logeval')
        keys.sort()
        new_keywords[i] = ','.join(keys) if len(keys) > 0 else None
        if len(conts) > 0:
            contributors[i] = ','.join(conts)
    logger.info('found {} loda programs and {} loda formulas'.format(num_loda_programs, num_loda_formulas))
    return (contributors, new_keywords, loda_formulas)


def create_database_schema(dbconn):
    schema = """
             CREATE TABLE IF NOT EXISTS seq_entries (
                 oeis_id               INTEGER  PRIMARY KEY NOT NULL,
                 name                  TEXT     NOT NULL,
                 keywords              TEXT     NOT NULL,
                 contributors          TEXT     NOT NULL,
                 loda_formula          TEXT     NOT NULL
             );
             """
    dbconn.execute(schema)


def insert_new_entries(dbconn, num_entries):
    query = 'SELECT max(oeis_id) FROM seq_entries;'
    dbcursor = dbconn.execute(query)
    current_max_id = int(dbcursor.fetchone()[0])
    if current_max_id >= num_entries:
        return
    new_entries = [ (id,'','','','') for id in range(current_max_id + 1, num_entries) ]
    logger.info('inserting {} new entries'.format(len(new_entries)))
    query = 'INSERT INTO seq_entries (oeis_id, name, keywords, contributors, loda_formula) VALUES (?, ?, ?, ?, ?);'
    dbconn.executemany(query, new_entries)
    dbconn.commit()


def update_entries(dbconn, column, values, batch_size = 10000):
    query = 'UPDATE seq_entries SET {} = ? WHERE oeis_id = ?;'.format(column)
    batch = []
    for i, k in enumerate(values):
        if not k:
            continue
        batch.append((k, i))
        if len(batch) == batch_size or i == len(values) - 1:
            logger.info('updating {} for entries {}-{}'.format(column, i-batch_size, i))
            dbconn.executemany(query, batch)
            dbconn.commit()
            batch = []


def main():
    loda_programs_path = update_loda()
    (inceval_programs, logeval_programs) = load_stats()

    names = fetch_list('names')
    min_size = len(names)
    authors = fetch_list('authors', min_size)
    comments = fetch_list('comments', min_size)
    formulas = fetch_list('formulas', min_size)
    keywords = fetch_list('keywords', min_size)
    programs = fetch_list('programs', min_size)

    (contributors, keywords, loda_formulas) = extract_details(names, authors, comments, formulas, keywords, programs,
                                                              inceval_programs, logeval_programs, loda_programs_path)

    logger.info('updating database')
    try:
        dbconn = sqlite3.connect('seqs.sqlite3')
        create_database_schema(dbconn)
        insert_new_entries(dbconn, len(names))
        update_entries(dbconn, 'name', names)
        update_entries(dbconn, 'contributors', contributors)
        update_entries(dbconn, 'keywords', keywords)
        update_entries(dbconn, 'loda_formula', loda_formulas)
    except sqlite3.Error as error:
        logger.error('error while connecting to sqlite', error)
    finally:
        if dbconn:
            dbconn.close()


if __name__ == "__main__":
    main()
