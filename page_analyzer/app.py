from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import page_analyzer.database as database
import requests
from validators.url import url as valid_url

from flask import Flask, render_template, request, flash, \
    redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.get("/")
def get_index():
    return render_template("index.html")


@app.post("/urls")
def post_urls():
    u = request.form.to_dict()["url"]
    url = validate_url(u)
    if url:
        print("Posting... " + url)
        if database.post_url(url):
            msg_category = "success"
            msg_message = "Страница успешно добавлена"
            flash(msg_message, msg_category)
        else:
            msg_category = "success"
            # msg_message = "Страница успешно добавлена"
            msg_message = "Страница уже существует"
            flash(msg_message, msg_category)

        id = database.get_url_by_name(url)["id"]
        return redirect(url_for("get_url", id=id))

    else:
        msg_category = "danger"
        msg_message = "Некорректный URL"
        flash(msg_message, msg_category)
        url = url if url else ""
        return render_template("index.html", url=u), 422


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
    url = database.get_url_by_id(id)
    if not url:
        return render_template("url_notfound.html")

    history = database.get_url_history(id)

    return render_template("url_details.html",
                           url=url, history=history)


@app.post("/urls/<id>/checks")
def post_url_checks(id):
    id = int(id)
    url = database.get_url_by_id(id)
    if url:
        url = url["name"]
    else:
        return render_template("url_notfound.html")

    try:
        url_status = check_url(url)
        url_status["id"] = id
    except requests.exceptions.RequestException:
        msg_category = "danger"
        msg_message = "Произошла ошибка при проверке"
        flash(msg_message, msg_category)
        return redirect(url_for("get_url", id=id))

    database.post_url_status(url_status)

    msg_category = "success"
    msg_message = "Страница успешно проверена"
    flash(msg_message, msg_category)

    return redirect(url_for("get_url", id=id))


def check_url(url):
    try:
        response = requests.get(url)
        status_code = response.status_code
        response.raise_for_status()
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        h1 = soup.h1.text if soup.h1 else ""
        title = soup.title.text if soup.title else ""
        description = ""
        for meta in soup.find_all("meta"):
            if meta.get("name") == "description":
                description = meta.get("content")
                break
        return {
            "url": url,
            "status_code": status_code,
            "h1": h1,
            "title": title,
            "description": description,
            "created_at": datetime.today()
        }

    except Exception as e:
        print(e)
        raise e


@app.get("/urls")
def get_urls():
    urls = database.get_urls()
    return render_template("urls_list.html", urls=urls)
