import time
import re
from playwright.sync_api import Playwright, sync_playwright, expect

from page_actions import filer_by_date_posted, filter_by_programming_languages, search_for_jobs
from models import JobPosting, DatePostedOptions, ProgrammingLanguageOption

BASE_URL = "https://ca.indeed.com"
JOB_ID_PARAM_PATTERN = "&vjk=[a-zA-Z0-9]+"


def run(p: Playwright) -> None:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()

    page.goto(BASE_URL)

    time.sleep(1)

    search_for_jobs(page, "front end developer", "Toronto, ON")

    # # a client-side redirect occurs where the job id of the first listed job is appended as a query param of "vjk"
    job_search_page = rf"{BASE_URL}/jobs?q=front+end+developer&l=Toronto%2C+ON"

    expect(page).to_have_url(
        re.compile(f"{re.escape(job_search_page)}&from=searchOnHP{JOB_ID_PARAM_PATTERN}")
    )

    selected_date_posted_option = DatePostedOptions.LAST_WEEK
    filer_by_date_posted(page, selected_date_posted_option)
    page.get_by_label("close", exact=True).click()  # close subscribe to updates modal

    num_days_query_value = selected_date_posted_option.value.days
    from_age_query = f"&fromage={num_days_query_value}"

    expect(page).to_have_url(
        re.compile(f"{re.escape(job_search_page)}&radius=50{from_age_query}{JOB_ID_PARAM_PATTERN}")
    )

    filter_by_programming_languages(page, [
        ProgrammingLanguageOption.Node_JS,
        ProgrammingLanguageOption.JavaScript,
        ProgrammingLanguageOption.HTML5,
        ProgrammingLanguageOption.CSS,
        ProgrammingLanguageOption.React,
    ])

    expect(page).to_have_url(
        re.compile(f"{re.escape(job_search_page)}{from_age_query}&sc=.+{JOB_ID_PARAM_PATTERN}")
    )

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
