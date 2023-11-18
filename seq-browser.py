import flask
import re
import sqlite3
import keywords

app = flask.Flask(__name__)


def get_db_connection():
    if 'db' not in flask.g:
        db = sqlite3.connect('file:seqs.sqlite3?mode=ro', uri=True)
        db.row_factory = sqlite3.Row
        flask.g.db = db
    return flask.g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()


@app.context_processor
def utility_processor():

    def a_number(id):
        return 'A' + str(id).zfill(6)

    def prog_links(entry):
        id = entry['oeis_id']
        keywords = entry['keywords'].split(',')
        links = []
        # if 'java' in keywords:
        #     links.append('<a target="_blank" href="https://github.com/archmageirvine/joeis/blob/master/src/irvine/oeis/a{:03}/A{:06}.java">Java</a>'.format(int(id/1000), id))
        if 'loda' in keywords:
            links.append('<a target="_blank" href="https://loda-lang.org/edit/?oeis={}">LODA</a>'.format(id))
        if len(links)>0:
            return '{}'.format(', '.join(links))
        return ''

    def select_keyword(k, active_keywords):
        if isinstance(active_keywords, str):
            for s in active_keywords.split(','):
                if s == k:
                    return '+' + k
                elif s == '-' + k:
                    return s
        return k

    def style_keyword(k, active_keywords):
        s = select_keyword(k, active_keywords=active_keywords)
        if len(s) > 0:
            if s[0] == '+':
                return 'plus'
            elif s[0] == '-':
                return 'minus'
        return 'default'

    def switch_keyword(k, active_keywords):
        if not isinstance(active_keywords, str):
            return k
        new_keywords = []
        found = False
        for s in active_keywords.split(','):
            if len(s.strip()) == 0:
                continue
            if s == k:
                new_keywords.append('-' + s)
                found = True
            elif s == '-' + k:
                found = True
            else:
                new_keywords.append(s)
        if not found:
            new_keywords.append(k)
        new_keywords.sort()
        return ','.join(new_keywords)

    return dict(a_number=a_number,
                prog_links=prog_links,
                select_keyword=select_keyword,
                style_keyword=style_keyword,
                switch_keyword=switch_keyword)


@app.route('/')
def index():
    db = get_db_connection()
    start = flask.request.args.get('start')
    if start:
        start = max(int(start),1)
    else:
        start = 1
    active_keywords = flask.request.args.get('keywords')
    search = flask.request.args.get('search')
    if not search:
        search = ''
    conditions = []
    if not active_keywords:
        active_keywords = ''
    for k in active_keywords.split(','):
        k = k.strip().lower()
        if len(k) == 0:
            continue
        if k[0]=='-':
            conditions.append('keywords NOT LIKE \'%{}%\''.format(k[1:]))
        else:
            conditions.append('keywords LIKE \'%{}%\''.format(k))
    if not search:
        search = ''
    if len(search) > 0:
        s = search.strip().lower()
        id_cond = ''
        if re.match(r"a[0-9]+", s):
            id = int(s[1:])
            id_cond = 'oeis_id = {} OR'.format(id)
        conditions.append('({} LOWER(name) LIKE "%{}%" OR LOWER(contributors) LIKE "%{}%")'.format(id_cond, s, s))
    where = ''
    if len(conditions) > 0:
        where = 'WHERE {}'.format(' AND '.join(conditions))
        print(where)
    count = db.execute('SELECT count(*) FROM seq_entries {}'.format(where)).fetchall()[0][0]
    batch = 100
    entries = db.execute('SELECT * FROM seq_entries {} LIMIT {} OFFSET {}'.format(where, batch, start-1)).fetchall()
    end = min(count, start - 1 + batch)
    return flask.render_template('index.html',
                                 search=search,
                                 batch=batch,
                                 count=count,
                                 start=start,
                                 end=end,
                                 entries=entries,
                                 all_keywords=keywords.get_keywords(),
                                 keyword_descriptions=keywords.get_keyword_descriptions(),
                                 active_keywords=active_keywords)

@app.route('/robots.txt')
def noindex():
    r = flask.Response(response="User-Agent: *\nDisallow: /\n", status=200, mimetype="text/plain")
    r.headers["Content-Type"] = "text/plain; charset=utf-8"
    return r
