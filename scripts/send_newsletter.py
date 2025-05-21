import os
from pathlib import Path
from datetime import datetime
import requests

try:
    from dotenv import load_dotenv
except ImportError:  # fallback if python-dotenv isn't installed
    load_dotenv = None

try:
    from jinja2 import Template
except ImportError:  # fallback if jinja2 isn't installed
    Template = None


def load_env():
    if load_dotenv:
        load_dotenv()


def parse_article(file_path: Path) -> dict:
    """Parse a markdown article with YAML front matter."""
    data = {"title": "Untitled", "date": "", "link": "", "source": "", "summary": ""}
    lines = file_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        data["summary"] = "\n".join(lines)
        return data
    meta_lines = []
    body_lines = []
    in_meta = True
    for line in lines[1:]:
        if in_meta:
            if line.strip() == "---":
                in_meta = False
                continue
            meta_lines.append(line)
        else:
            body_lines.append(line)
    for ml in meta_lines:
        if ":" in ml:
            key, value = ml.split(":", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    data["summary"] = "\n".join(body_lines).strip()
    return data


def load_articles(directory: Path, limit: int = 5) -> list[dict]:
    """Load the latest articles from a directory."""
    articles = []
    for path in sorted(directory.glob("*.md"), reverse=True):
        articles.append(parse_article(path))
        if len(articles) >= limit:
            break
    return articles


DEFAULT_TEMPLATE = """\
<h1>Weekly Newsletter</h1>
<ul>
{% for article in articles %}
  <li><a href="{{ article.link }}">{{ article.title }}</a> - {{ article.date }}</li>
{% endfor %}
</ul>
"""


def render_newsletter(articles: list[dict]) -> str:
    template_path = Path("templates/newsletter.html")
    if template_path.exists():
        template_str = template_path.read_text(encoding="utf-8")
    else:
        template_str = DEFAULT_TEMPLATE
    if Template is None:
        return template_str
    return Template(template_str).render(articles=articles)


def send_via_mailchimp(subject: str, html_content: str):
    api_key = os.getenv("MAILCHIMP_API_KEY")
    server_prefix = os.getenv("MAILCHIMP_SERVER_PREFIX")
    list_id = os.getenv("MAILCHIMP_LIST_ID")
    from_email = os.getenv("EMAIL_FROM")
    from_name = os.getenv("EMAIL_FROM_NAME", from_email)
    if not all([api_key, server_prefix, list_id, from_email]):
        print("Missing Mailchimp configuration. Exiting.")
        return
    base = f"https://{server_prefix}.api.mailchimp.com/3.0"
    auth = ("anystring", api_key)
    # create campaign
    resp = requests.post(
        f"{base}/campaigns",
        auth=auth,
        json={
            "type": "regular",
            "recipients": {"list_id": list_id},
            "settings": {
                "subject_line": subject,
                "from_name": from_name,
                "reply_to": from_email,
            },
        },
    )
    resp.raise_for_status()
    campaign_id = resp.json()["id"]
    # set content
    resp = requests.put(
        f"{base}/campaigns/{campaign_id}/content",
        auth=auth,
        json={"html": html_content},
    )
    resp.raise_for_status()
    # send campaign
    resp = requests.post(
        f"{base}/campaigns/{campaign_id}/actions/send",
        auth=auth,
    )
    resp.raise_for_status()
    print("Newsletter sent!")


def main():
    load_env()
    articles_dir = Path("_articles")
    if not articles_dir.exists():
        print(f"Directory {articles_dir} does not exist. Exiting.")
        return
    articles = load_articles(articles_dir)
    html_content = render_newsletter(articles)
    subject = f"Weekly Newsletter - {datetime.utcnow().strftime('%Y-%m-%d')}"
    send_via_mailchimp(subject, html_content)


if __name__ == "__main__":
    main()
