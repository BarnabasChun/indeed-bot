from typing import Pattern
from playwright.sync_api import Page


def filer_by_date_posted(page: Page) -> None:
    page.get_by_role("button", name="Date posted filter").click()
    page.get_by_role("link", name="Last 7 days").click()


def filter_by_programming_languages(page: Page, languages: list[str | Pattern[str]]) -> None:
    page.get_by_role("button", name="Programming language filter").click()

    programming_language_filter_modal = page.get_by_role("dialog", name="Edit Programming language filter selection")

    for language in languages:
        programming_language_filter_modal.get_by_text(language).click()

    page.get_by_role("button", name="Update").click()
