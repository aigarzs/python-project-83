from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import psycopg2.errorcodes as psyerrors
from validators.url import url as valid_url

from flask import Flask, render_template, request, flash, get_flashed_messages, \
    redirect, url_for
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

history = (
    {"id": 1,
     "code": 200,
     "h1": "Example Domain",
     "title": "Example Domain",
     "description": "",
     "created_at": "2024-06-17"},
    {"id": 1,
     "code": 200,
     "h1": "Example Domain",
     "title": "Example Domain",
     "description": "",
     "created_at": "2024-06-01"},
    {"id": 1,
     "code": 200,
     "h1": "Example Domain",
     "title": "Example Domain",
     "description": "",
     "created_at": "2024-05-15"}
)


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
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM urls WHERE id = %s;", (id,))
        data = cursor.fetchone()
        url = {"id": data[0],
               "name": data[1],
               "created_at": data[2]}
    except Exception as err:
        # msg_category = "danger"
        # msg_message = err
        # flash(msg_message, msg_category)
        # messages = get_flashed_messages(with_categories=True)
        return render_template("url_notfound.html")
    finally:
        cursor.close()
        connection.close()

    messages = get_flashed_messages(with_categories=True)
    return render_template("url_details.html", messages=messages,
                           url=url, history=history)


@app.post("/urls/<id>/checks")
def post_url_checks(id):
    msg_category = "success"
    msg_message = "Страница успешно проверена"
    flash(msg_message, msg_category)
    return redirect(url_for("get_url", id=id))


@app.get("/urls")
def get_urls():
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            sql = "SELECT id, name, created_at FROM urls;"
            cursor.execute(sql)
            data = cursor.fetchall()
            urls = []
            for r in data:
                url = {"id": r[0], "name": r[1], "created_at": r[2]}
                urls.append(url)
    return render_template("urls_list.html", urls=urls)
