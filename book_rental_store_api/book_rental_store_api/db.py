import sqlite3
from flask import g


DATABASE = '../../db.sqlite3'


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    
    db.row_factory = make_dicts
    return db


def query_db(query, args=()):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()