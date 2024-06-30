import re
from playwright.sync_api import Playwright, sync_playwright
import time

from page_actions import filer_by_date_posted, filter_by_programming_languages
from models import JobPosting


def run(p: Playwright) -> None:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()
    page.goto("https://ca.indeed.com/jobs?q=front+end+developer")

    time.sleep(1)  # wait for client-side redirect (adding of "vjk" query param)

    filer_by_date_posted(page)
    page.get_by_label("close", exact=True).click()  # close subscribe to updates modal
    filter_by_programming_languages(page, ["Node.js", "React", "JavaScript"])

    job_link_elements = page.get_by_role("button", name=re.compile("^full details of.*", re.IGNORECASE)).all()
    job_postings: list[JobPosting] = []

    for link in job_link_elements:
        job_title = link.text_content()

        if re.search(r"(?i)front[-\s]?end", job_title):
            job_postings.append(JobPosting(title=job_title, url=link.get_attribute("href")))
            continue

        # TODO: check for contents within posting to see if if keywords, "React", "Javascript", "Typescript", etc. exist

    page.pause()  # TODO: Remove after dev complete

    # # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
