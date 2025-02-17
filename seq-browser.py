import datetime
import flask
import flask_limiter
import os
import re
import sqlite3
import keywords



app = flask.Flask(__name__)

# Rate limiter disabled (configured in nginx)
#
# def get_ipaddr() -> str:
#     # Retrieve the client's IP address from the request
#     # X-Forwarded-For header is used to handle requests behind a proxy
#     ip_address = flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr)
#     return ip_address
# 
#limiter = flask_limiter.Limiter(
#    get_ipaddr,
#    app=app,
#    default_limits=['1000 per day', '100 per hour'],
#    storage_uri='memory://',
#)

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
        if 'loda' in keywords:
            links.append('<a target="_blank" href="https://loda-lang.org/edit/?oeis={}">LODA</a>'.format(id))
        if len(links)>0:
            return '{}'.format(', '.join(links))
        return ''

    def seq_description(entry, active_keywords):
        if 'loda-formula' in active_keywords and not '-loda-formula' in active_keywords:
            return entry['name'] + '<br>Formula: ' + entry['loda_formula']
        else:
            return entry['name']

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
                seq_description=seq_description,
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
        stripped = k[1:] if k[0] == '-' else k
        if not keywords.exists_keyword(stripped):
            return flask.abort(400, 'Invalid keyword: {}'.format(stripped))
        if k != stripped:
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
    count = db.execute('SELECT count(*) FROM seq_entries {}'.format(where)).fetchall()[0][0]
    batch = 100
    entries = db.execute('SELECT * FROM seq_entries {} LIMIT {} OFFSET {}'.format(where, batch, start-1)).fetchall()
    end = min(count, start - 1 + batch)
    mod_time = os.path.getmtime('seqs.sqlite3')
    last_updated = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
    return flask.render_template('index.html',
                                 search=search,
                                 batch=batch,
                                 count=count,
                                 start=start,
                                 end=end,
                                 entries=entries,
                                 all_keywords=keywords.get_keywords(),
                                 keyword_descriptions=keywords.get_keyword_descriptions(),
                                 active_keywords=active_keywords,
                                 last_updated=last_updated)

@app.route('/robots.txt')
def noindex():
    ua = flask.request.headers.get('User-Agent')
    app.logger.info("User-Agent requesting robots.txt: {}".format(ua))
    r = flask.Response(response="User-Agent: *\nDisallow: /\n", status=200, mimetype="text/plain")
    r.headers["Content-Type"] = "text/plain; charset=utf-8"
    return r
