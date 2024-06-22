import pytest
from page_analyzer import app
from playwright.sync_api import sync_playwright  # , Playwright


def test_app():
    print(app.config['SECRET_KEY'])


@pytest.mark.skip(reason="onrender.com is not working")
def test_add_new_site():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()  # or "firefox" or "webkit".
        page = browser.new_page()
        # page.goto("http://localhost:8000")
        page.goto("https://site-analyzer-uu2b.onrender.com")
        page.locator('input[name="url"]').type('http://stub.com/')
        page.locator('input[type="submit"]').click()
        msg1 = page.locator('text=Страница успешно добавлена').is_visible()
        msg2 = page.locator('text=Страница уже существует').is_visible()

        assert msg1 or msg2

        # other actions...
        browser.close()
