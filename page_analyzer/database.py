import os
from datetime import datetime

import psycopg2
import psycopg2.errorcodes as psyerrors


DATABASE_URL = os.getenv('DATABASE_URL')


def post_url(url):
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            try:
                sql = "INSERT INTO urls (name, created_at) VALUES (%s, %s);"
                params = (url, datetime.now())
                print(cursor.mogrify(sql, params))
                cursor.execute(sql, params)
                connection.commit()
                return True
            except psycopg2.Error as err:
                connection.rollback()
                if err.pgcode == psyerrors.UNIQUE_VIOLATION:
                    return False
                else:
                    raise err


def get_url_by_name(url):
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM urls WHERE name = %s;"
            print(cursor.mogrify(sql, (url,)))
            cursor.execute(sql, (url,))
            record = cursor.fetchone()
            if record:
                url = {"id": record[0],
                       "name": record[1],
                       "created_at": datetime.date(record[2])}
                return url
            else:
                return None


def get_url_by_id(id):
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM urls WHERE id = %s;"
            print(cursor.mogrify(sql, (id,)))
            cursor.execute(sql, (id,))
            record = cursor.fetchone()
            if record:
                url = {"id": record[0],
                       "name": record[1],
                       "created_at": datetime.date(record[2])}
                return url
            else:
                return None


def get_url_history(id):
    id = int(id)
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
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
            print(cursor.mogrify(sql, (id,)))
            cursor.execute(sql, (id,))
            data = cursor.fetchall()
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
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
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

            print(cursor.mogrify(sql, status))
            cursor.execute(sql, status)
            connection.commit()


def get_urls():
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            sql = """SELECT
            u.id,
            u.name,
            u.created_at,
            (SELECT status_code FROM url_checks AS c
            WHERE c.url_id = u.id ORDER BY c.created_at DESC
             LIMIT 1) AS status_code
            FROM urls AS u;"""
            print(sql)
            cursor.execute(sql)
            data = cursor.fetchall()

    urls = []
    for r in data:
        url = {"id": r[0],
               "name": r[1],
               "created_at": datetime.date(r[2]),
               "status_code": r[3]}
        urls.append(url)

    return urls
