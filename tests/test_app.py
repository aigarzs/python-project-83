from page_analyzer import app


def test_app():
    print(app.config['SECRET_KEY'])
