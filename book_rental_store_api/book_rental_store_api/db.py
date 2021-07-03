import sqlite3
from flask import g
from flask import current_app



def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
    
    db.row_factory = make_dicts
    return db


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def query_db(query, args=()):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_connection)