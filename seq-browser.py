import flask
import sqlite3
import keywords

app = flask.Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('seqs.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn


@app.context_processor
def utility_processor():

    def a_dir(id):
        return str(int(id/1000)).zfill(3)

    def a_number(id):
        return 'A' + str(id).zfill(6)

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

    return dict(a_dir=a_dir,
                a_number=a_number,
                select_keyword=select_keyword,
                style_keyword=style_keyword,
                switch_keyword=switch_keyword)


@app.route('/')
def index():
    conn = get_db_connection()
    active_keywords = flask.request.args.get('keywords')
    where = ''
    if isinstance(active_keywords, str):
        keyword_index = keywords.keywords_to_index()
        positive_bits = 0
        negative_bits = 0
        for k in active_keywords.split(','):
            k = k.strip()
            if len(k) == 0:
                continue
            if k[0]=='-':
                r = k[1:]
                if r in keyword_index:
                    negative_bits += 1 << keyword_index[r]
            elif k in keyword_index:
                positive_bits += 1 << keyword_index[k]
        conditions = []
        if positive_bits > 0:
            conditions.append('keywords & {} = {}'.format(positive_bits,positive_bits))
        if negative_bits > 0:
            conditions.append('keywords & {} = 0'.format(negative_bits))
        if len(conditions)>0:
            where = 'WHERE {}'.format(' AND '.join(conditions))
    print(where)
    limit = 10
    count = conn.execute('SELECT count(*) FROM seq_entries {}'.format(where)).fetchall()[0][0]
    show = min(count, limit)
    entries = conn.execute('SELECT * FROM seq_entries {} LIMIT {}'.format(where,limit)).fetchall()
    conn.close()
    return flask.render_template('index.html',
                                 count=count,
                                 show=show,
                                 entries=entries,
                                 oeis_keywords=keywords.get_oeis_keywords(),
                                 active_keywords=active_keywords)
