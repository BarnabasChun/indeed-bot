from playwright.sync_api import Page

from models import DatePostedOption, ProgrammingLanguageOption


def search_for_jobs(page: Page, title: str, city: str):
    page.get_by_placeholder("Job title, keywords, or").fill(title)
    page.get_by_placeholder("City, province, or \"remote\"").fill(city)
    page.get_by_role("button", name="Find jobs").click()


def filer_by_date_posted(page: Page, date_posted_option: DatePostedOption) -> None:
    page.get_by_role("button", name="Date posted filter").click()

    page.get_by_role("link", name=date_posted_option.value.label).click()


def filter_by_programming_languages(page: Page, languages: list[ProgrammingLanguageOption]) -> None:
    page.get_by_role("button", name="Programming language filter").click()

    programming_language_filter_modal = page.get_by_role("dialog", name="Edit Programming language filter selection")

    for language in languages:
        programming_language_filter_modal.get_by_text(language.value).click()

    page.get_by_role("button", name="Update").click()
