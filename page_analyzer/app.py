import psycopg2
import requests
import page_analyzer.database as database
import page_analyzer.urls as urls
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, \
    redirect, url_for
import os


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.get("/")
def get_index():
    return render_template("index.html"), 200


@app.post("/urls")
def post_urls():
    u = request.form.to_dict()["url"]
    url = urls.validate_and_normalize(u)
    if url:
        try:
            id = database.post_url(url)["id"]
            flash("Страница успешно добавлена", "success")
        except psycopg2.Error:
            flash("Страница уже существует", "success")
            id = database.get_url_by_name(url)["id"]

        return redirect(url_for("get_url", id=id))

    else:
        flash("Некорректный URL", "danger")
        return render_template("index.html", url=u), 422


@app.get("/urls/<id>")
def get_url(id):
    try:
        id = int(id)
    except Exception:
        return render_template("url_notfound.html"), 404

    url = database.get_url_by_id(id)
    if not url:
        return render_template("url_notfound.html"), 404

    history = database.get_url_history(id)

    return render_template("url_details.html",
                           url=url, history=history), 200


@app.post("/urls/<id>/checks")
def post_url_checks(id):
    id = int(id)
    url = database.get_url_by_id(id)
    if url:
        url = url["name"]
    else:
        return render_template("url_notfound.html"), 404

    try:
        response = requests.get(url)
        status_code = response.status_code
        response.raise_for_status()
        content = response.content
        url_seo = urls.extract_seo_data(content)
        url_seo["id"] = id
        url_seo["url"] = url
        url_seo["status_code"] = status_code

    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", "danger")
        url = database.get_url_by_id(id)
        history = database.get_url_history(id)
        return render_template("url_details.html",
                               url=url, history=history), 422

    database.post_url_seo(url_seo)

    flash("Страница успешно проверена", "success")

    return redirect(url_for("get_url", id=id))


@app.get("/urls")
def get_urls():
    urls_list = database.get_urls()
    return render_template("urls_list.html", urls=urls_list), 200
