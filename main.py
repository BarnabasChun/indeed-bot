import re
from playwright.sync_api import Playwright, sync_playwright, expect

from page_actions import filer_by_date_posted, filter_by_programming_languages
from models import JobPosting, DatePostedOptions, ProgrammingLanguageOption

BASE_URL = "https://ca.indeed.com"
JOB_SEARCH_PAGE = rf"{BASE_URL}/jobs?q=front+end+developer&l=Toronto%2C+ON&radius=50"
JOB_ID_PARAM_PATTERN = "&vjk=[a-zA-Z0-9]+"


def run(p: Playwright) -> None:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()

    page.goto(JOB_SEARCH_PAGE)

    # a client-side redirect occurs where the job id of the first listed job is appended as a query param of "vjk"
    expect(page).to_have_url(re.compile(f"{re.escape(JOB_SEARCH_PAGE)}{JOB_ID_PARAM_PATTERN}"))

    selected_date_posted_option = DatePostedOptions.LAST_WEEK
    filer_by_date_posted(page, selected_date_posted_option)

    num_days_query_value = selected_date_posted_option.value.days
    expect(page).to_have_url(
        re.compile(f"{re.escape(JOB_SEARCH_PAGE)}&fromage={num_days_query_value}{JOB_ID_PARAM_PATTERN}")
    )

    page.get_by_label("close", exact=True).click()  # close subscribe to updates modal

    filter_by_programming_languages(page, [
        ProgrammingLanguageOption.Node_JS,
        ProgrammingLanguageOption.JavaScript,
        ProgrammingLanguageOption.HTML5,
        ProgrammingLanguageOption.CSS,
        ProgrammingLanguageOption.React,
    ])

    # TODO: expect page to also have params related to selected programming languages

    job_link_elements = page.get_by_role("button", name=re.compile("^full details of.*", re.IGNORECASE)).all()
    job_postings: list[JobPosting] = []

    for link_element in job_link_elements:
        job_title = link_element.text_content()

        if re.search(r"(?i)front[-\s]?end", job_title):
            job_postings.append(JobPosting(title=job_title, url=link_element.get_attribute("href")))
            continue

        # TODO: check for contents within posting to see if if keywords, "React", "Javascript", "Typescript", etc. exist

    page.pause()  # TODO: Remove after dev complete

    # # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
