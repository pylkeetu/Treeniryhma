import sqlite3

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def query(sql, params=None):
    if params is None:
        params = []

    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result


def execute(sql, params=None):
    if params is None:
        params = []

    con = get_connection()
    cur = con.execute(sql, params)
    con.commit()
    last_id = cur.lastrowid
    con.close()
    return last_id