import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        yield browser
        browser.close()


def test_homepage(browser):
    page = browser.new_page()
    page.goto("http://django:8000/")
    assert "ScaleOS.net - Your next-gen software" in page.title()
