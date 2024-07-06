import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def db_execute(commit=True, fetch_results=None):
    def inner(func):
        def wrapper(*args, **kwargs):
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    inner_args = func(*args, **kwargs)
                    sql = inner_args["sql"]
                    params = inner_args["params"]
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
        return wrapper
    return inner


@db_execute(commit=True, fetch_results="fetchone")
def add_url(url):
    sql = """INSERT INTO urls (name)
        VALUES (%s)
        RETURNING id;"""
    params = (url, )
    return {"sql": sql,
            "params": params}


@db_execute(commit=False, fetch_results="fetchone")
def get_url_by_name(url):
    sql = "SELECT * FROM urls WHERE name = %s;"
    params = (url,)
    return {"sql": sql,
            "params": params}


@db_execute(commit=False, fetch_results="fetchone")
def get_url_by_id(id):
    sql = "SELECT * FROM urls WHERE id = %s;"
    params = (id,)
    return {"sql": sql,
            "params": params}


@db_execute(commit=False, fetch_results="fetchall")
def get_url_history_by_url_id(id):
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
            "params": params}


@db_execute(commit=True, fetch_results=None)
def post_url_seo(seo):
    sql = """INSERT INTO url_checks (
            url_id,
            status_code,
            h1,
            title,
            description
            )
         VALUES (
         %(id)s,
         %(status_code)s,
         %(h1)s,
         %(title)s,
         %(description)s
         );"""

    return {"sql": sql,
            "params": seo}


@db_execute(commit=False, fetch_results="fetchall")
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
            "params": None}
