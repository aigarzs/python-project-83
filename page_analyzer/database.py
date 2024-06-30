import os
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def db_execute(func):
    def inner(*args, **kwargs):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                inner_args = func(*args, **kwargs)
                sql = inner_args["sql"]
                params = inner_args["params"]
                commit = inner_args["commit"]
                fetch_results = inner_args["fetch_results"]
                try:
                    cursor.execute(sql, params)
                    if commit:
                        conn.commit()
                    if fetch_results == "fetchone":
                        return cursor.fetchone()
                    elif fetch_results == "fetchall":
                        return cursor.fetchall()
                except psycopg2.Error as err:
                    if commit:
                        conn.rollback()
                    raise err

    return inner


@db_execute
def post_url(url):
    sql = """INSERT INTO urls (name, created_at)
        VALUES (%s, %s)
        RETURNING id;"""
    params = (url, datetime.now())
    return {"sql": sql,
            "params": params,
            "commit": True,
            "fetch_results": "fetchone"}


@db_execute
def get_url_by_name(url):
    sql = "SELECT * FROM urls WHERE name = %s;"
    params = (url,)
    return {"sql": sql,
            "params": params,
            "commit": False,
            "fetch_results": "fetchone"}


@db_execute
def get_url_by_id(id):
    sql = "SELECT * FROM urls WHERE id = %s;"
    params = (id,)
    return {"sql": sql,
            "params": params,
            "commit": False,
            "fetch_results": "fetchone"}


@db_execute
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
    return {"sql": sql,
            "params": params,
            "commit": False,
            "fetch_results": "fetchall"
            }


@db_execute
def post_url_seo(seo):
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

    return {"sql": sql,
            "params": seo,
            "commit": True,
            "fetch_results": None}


@db_execute
def get_urls():
    sql = """SELECT
            u.id,
            u.name,
            u.created_at,
            (SELECT status_code FROM url_checks AS c
            WHERE c.url_id = u.id ORDER BY c.created_at DESC
             LIMIT 1) AS status_code
            FROM urls AS u;"""
    return {"sql": sql,
            "params": None,
            "commit": False,
            "fetch_results": "fetchall"
            }
