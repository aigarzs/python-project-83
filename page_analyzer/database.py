import os
from datetime import datetime

import psycopg2
import psycopg2.errorcodes as psyerrors
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def db_cursor_execute(sql, params, fetch_results=False):
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql, params)
                connection.commit()
                if fetch_results:
                    records = cursor.fetchall()
                    return records
            except psycopg2.Error as err:
                connection.rollback()
                raise err


def post_url(url):
    try:
        sql = """INSERT INTO urls (name, created_at)
        VALUES (%s, %s)
        RETURNING id;"""
        params = (url, datetime.now())
        records = db_cursor_execute(sql, params, True)
        if records:
            return records[0][0]
        else:
            return False
    except psycopg2.Error as err:
        if err.pgcode == psyerrors.UNIQUE_VIOLATION:
            return False
        else:
            raise err


def get_url_by_name(url):
    sql = "SELECT * FROM urls WHERE name = %s;"
    params = (url,)
    records = db_cursor_execute(sql, params, True)
    record = records[0] if records else None
    if record:
        url = {"id": record[0],
               "name": record[1],
               "created_at": datetime.date(record[2])}
        return url
    else:
        return None


def get_url_by_id(id):
    sql = "SELECT * FROM urls WHERE id = %s;"
    params = (id,)
    records = db_cursor_execute(sql, params, True)
    record = records[0] if records else None
    if record:
        url = {"id": record[0],
               "name": record[1],
               "created_at": datetime.date(record[2])}
        return url
    else:
        return None


def get_url_history(id):
    id = int(id)
    sql = ("SELECT "
           "id, "
           "status_code, "
           "h1, "
           "title, "
           "description, "
           "created_at"
           " FROM url_checks "
           " WHERE url_id = %s "
           " ORDER BY created_at DESC;")
    params = (id,)
    data = db_cursor_execute(sql, params, True)
    history = []
    if data:
        for r in data:
            h = {
                "id": r[0],
                "status_code": r[1],
                "h1": r[2],
                "title": r[3],
                "description": r[4],
                "created_at": datetime.date(r[5])
            }
            history.append(h)

    return history


def post_url_status(status):
    sql = """INSERT INTO url_checks (
            url_id,
            status_code,
            h1,
            title,
            description,
            created_at
            )
         VALUES (
         %(id)s,
         %(status_code)s,
         %(h1)s,
         %(title)s,
         %(description)s,
         %(created_at)s
         );"""

    db_cursor_execute(sql, status)


def get_urls():
    sql = """SELECT
            u.id,
            u.name,
            u.created_at,
            (SELECT status_code FROM url_checks AS c
            WHERE c.url_id = u.id ORDER BY c.created_at DESC
             LIMIT 1) AS status_code
            FROM urls AS u;"""
    data = db_cursor_execute(sql, None, True)
    urls = []
    for r in data:
        url = {"id": r[0],
               "name": r[1],
               "created_at": datetime.date(r[2]),
               "status_code": r[3]}
        urls.append(url)

    return urls
