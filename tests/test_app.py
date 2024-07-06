from page_analyzer.app import app


def test_secret_code_set():
    print(app.config.get("SECRET_KEY"))
