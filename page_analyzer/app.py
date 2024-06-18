from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import psycopg2.errorcodes as psyerrors
import requests
from validators.url import url as valid_url

from flask import Flask, render_template, request, flash, \
    get_flashed_messages, \
    redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.get("/")
def get_index():
    return render_template("index.html")


@app.post("/urls")
def post_urls():
    u = request.form.to_dict()["url"]
    url = validate_url(u)
    if url:
        print("Processing... " + url)
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO urls (name, created_at) "
                                   "VALUES (%s, %s);", (url, datetime.now()))
                    connection.commit()
                    msg_category = "success"
                    msg_message = "Страница успешно добавлена"
                    flash(msg_message, msg_category)
                except psycopg2.Error as err:
                    connection.rollback()
                    if not err.pgcode == psyerrors.UNIQUE_VIOLATION:
                        msg_category = "danger"
                        msg_message = err
                        flash(msg_message, msg_category)

                sql = "SELECT id FROM urls WHERE name = %s;"
                print(cursor.mogrify(sql, (url,)))
                cursor.execute(sql, (url,))
                id = cursor.fetchone()[0]
        return redirect(url_for("get_url", id=id))

    else:
        msg_category = "danger"
        msg_message = "Некорректный URL"
        flash(msg_message, msg_category)
        messages = get_flashed_messages(with_categories=True)
        url = url if url else ""
        return render_template("index.html", messages=messages, url=url)


def validate_url(address):
    if valid_url(address):
        o = urlparse(address)
        if o.scheme and o.netloc:
            return o.scheme + "://" + o.netloc
        else:
            return False
    else:
        return False


@app.get("/urls/<id>")
def get_url(id):
    id = int(id)
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM urls WHERE id = %s;", (id,))
                data = cursor.fetchone()
                url = {"id": data[0],
                       "name": data[1],
                       "created_at": data[2]}
            except Exception:
                return render_template("url_notfound.html")

            history = []
            try:
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
                cursor.execute(sql, (id,))
                data = cursor.fetchall()
                for r in data:
                    h = {
                        "id": r[0],
                        "status_code": r[1],
                        "h1": r[2],
                        "title": r[3],
                        "description": r[4],
                        "created_at": r[5]
                    }
                    history.append(h)
            except Exception:
                pass

    messages = get_flashed_messages(with_categories=True)
    return render_template("url_details.html", messages=messages,
                           url=url, history=history)


@app.post("/urls/<id>/checks")
def post_url_checks(id):
    id = int(id)
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            try:
                sql = """SELECT name FROM urls
                     WHERE id = %s
                    """
                cursor.execute(sql, (id,))
                url = cursor.fetchone()[0]
            except Exception:
                return render_template("url_notfound.html")

            try:
                status_code = check_url_status(url)
            except requests.exceptions.RequestException:
                msg_category = "danger"
                msg_message = "Произошла ошибка при проверке"
                flash(msg_message, msg_category)
                return redirect(url_for("get_url", id=id))

            sql = """INSERT INTO url_checks (url_id, status_code, created_at)
             VALUES (%s, %s, %s);"""
            data = (id, status_code, datetime.now())
            print(cursor.mogrify(sql, data))
            cursor.execute(sql, data)
            connection.commit()

    msg_category = "success"
    msg_message = "Страница успешно проверена"
    flash(msg_message, msg_category)

    return redirect(url_for("get_url", id=id))


def check_url_status(url):
    try:
        response = requests.get(url)
        status_code = response.status_code
        print(url + " status code:" + str(status_code))
        response.raise_for_status()
    except Exception as e:
        print(e)
        raise e

    return status_code


@app.get("/urls")
def get_urls():
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            sql = """select
            u.id,
            u.name,
            u.created_at,
            (select status_code from url_checks as c
            where c.url_id = u.id order by c.created_at desc
             limit 1) as status_code
            from urls as u;"""
            cursor.execute(sql)
            data = cursor.fetchall()
            urls = []
            for r in data:
                url = {"id": r[0],
                       "name": r[1],
                       "created_at": r[2],
                       "status_code": r[3]}
                urls.append(url)
    return render_template("urls_list.html", urls=urls)
