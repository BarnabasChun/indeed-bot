import time
import re
import random
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError, Page

from email_helpers import email_job_postings
from page_actions import filer_by_date_posted, filter_by_programming_languages, search_for_jobs
from models import JobPosting, DatePostedOption, ProgrammingLanguageOption

BASE_URL = "https://ca.indeed.com"
JOB_ID_PARAM_PATTERN = "&vjk=[a-zA-Z0-9]+"
load_dotenv()


def scrape_job_postings(page: Page) -> list[JobPosting]:
    job_postings: list[JobPosting] = []

    while True:
        job_link_elements = page.get_by_role("button", name=re.compile("^full details of.*", re.IGNORECASE)).all()

        for i, link_element in enumerate(job_link_elements):
            job_title = link_element.text_content()
            link_path = link_element.get_attribute("href")
            link_url = f"{BASE_URL}{link_path}"
            company_name = page.get_by_test_id("inlineHeader-companyName").inner_text()

            if re.search(r"(?i)front[-\s]?end", job_title):
                job_postings.append(
                    JobPosting(
                        title=job_title,
                        url=link_url,
                        company_name=company_name
                    )
                )
                print(f"Job posting matching desired title found: {job_title} at {company_name}")
                continue

            if i > 0:
                random_delay = random.uniform(0.6, 1.2)
                time.sleep(random_delay)
                link_element.click()
                try:
                    expect(page.get_by_test_id("jobsearch-JobInfoHeader-title")).to_contain_text(job_title)
                except AssertionError as e:
                    print(f"Error while checking that job posting loaded: {e}")
                    break

            job_description = page.locator("#jobDescriptionText")

            if re.search(r'\b(React|JavaScript|TypeScript|Node)\b', job_description.text_content()):
                print(f"Job posting matching desired keywords found: {job_title} at {company_name}")
                job_postings.append(
                    JobPosting(
                        title=job_title,
                        url=link_url,
                        company_name=company_name
                    )
                )

        try:
            page.get_by_test_id("pagination-page-next").click(timeout=2000)
        except TimeoutError:
            print("reached last page")
            break

    return job_postings


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

    selected_date_posted_option = DatePostedOption.LAST_WEEK
    filer_by_date_posted(page, selected_date_posted_option)
    page.get_by_label("close", exact=True).click()  # close subscribe to updates modal

    num_days_query_value = selected_date_posted_option.value.days
    from_age_query = f"&fromage={num_days_query_value}"

    expect(page).to_have_url(
        re.compile(f"{re.escape(job_search_page)}(&radius=50)?{from_age_query}{JOB_ID_PARAM_PATTERN}")
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

    job_postings = scrape_job_postings(page)
    email_job_postings(job_postings)

    # # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
