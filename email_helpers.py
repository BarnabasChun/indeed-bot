import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from models import JobPosting


def generate_email_body(job_postings: list[JobPosting]) -> str:
    email_body = f"""
        <html>
        <body>
            <ol>
                {''.join(f'<li><a href="{job.url}">{job.title}</a> at {job.company_name}</li>' for job in job_postings)}
            </ol>
        </body>
        </html>
        """

    return email_body


def email_job_postings(job_postings: list[JobPosting]) -> None:
    from_email = os.getenv('FROM_EMAIL')
    to_email = os.getenv('TO_EMAIL')
    pw = os.getenv('PASSWORD')

    email_body = generate_email_body(job_postings)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Job Postings' # TODO add date info based on selected DatePostedOptions
    msg.attach(MIMEText(email_body, 'html'))

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(user=from_email, password=pw)
        connection.send_message(msg)

    print(f"Finished emailing job postings to {to_email}")
