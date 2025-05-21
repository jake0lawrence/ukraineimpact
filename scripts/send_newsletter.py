import os
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_SERVER_PREFIX = os.getenv("MAILCHIMP_SERVER_PREFIX")
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")
TEMPLATE_DIR = Path(os.getenv("TEMPLATE_DIR", "templates"))
ARTICLES_DIR = Path(os.getenv("OUTPUT_DIR", "website/_articles"))
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")


def gather_articles():
    articles = []
    if ARTICLES_DIR.exists():
        for md_file in sorted(ARTICLES_DIR.glob("*.md"), key=os.path.getmtime, reverse=True):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            articles.append({"filename": md_file.name, "content": content})
    return articles


def render_email(articles):
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("newsletter.html")
    return template.render(date=datetime.utcnow().strftime("%Y-%m-%d"), articles=articles)


def send_via_mailchimp(subject, html):
    if not all([MAILCHIMP_API_KEY, MAILCHIMP_SERVER_PREFIX, MAILCHIMP_LIST_ID]):
        print("Mailchimp configuration missing. Skipping send.")
        return
    base_url = f"https://{MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0"
    data = {
        "type": "regular",
        "recipients": {"list_id": MAILCHIMP_LIST_ID},
        "settings": {
            "subject_line": subject,
            "title": subject,
            "from_name": "Newsletter",
            "reply_to": FROM_EMAIL,
        },
    }
    r = requests.post(
        f"{base_url}/campaigns",
        auth=("anystring", MAILCHIMP_API_KEY),
        json=data,
    )
    r.raise_for_status()
    campaign_id = r.json().get("id")

    content_data = {"html": html}
    requests.put(
        f"{base_url}/campaigns/{campaign_id}/content",
        auth=("anystring", MAILCHIMP_API_KEY),
        json=content_data,
    ).raise_for_status()

    requests.post(
        f"{base_url}/campaigns/{campaign_id}/actions/send",
        auth=("anystring", MAILCHIMP_API_KEY),
    ).raise_for_status()
    print(f"Newsletter sent: {subject}")


def main():
    articles = gather_articles()
    if not articles:
        print("No articles found to include in the newsletter.")
        return
    subject = f"Weekly Newsletter - {datetime.utcnow().strftime('%Y-%m-%d')}"
    html = render_email(articles)
    send_via_mailchimp(subject, html)


if __name__ == "__main__":
    main()
