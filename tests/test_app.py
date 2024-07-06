from page_analyzer.app import app


def test_secret_code_set():
    assert app.config.get("SECRET_KEY")
