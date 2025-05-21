# RSS Feed Newsletter

This project fetches articles from one or more RSS feeds and lets you send them as a weekly email via Mailchimp. Articles are saved as Markdown files so they can be re‑used for a future website.

## Features

- Fetch RSS feeds listed in an environment variable and store them under `_articles/`.
- Render a newsletter using Jinja2 (or a plain HTML fallback) and send it with the Mailchimp API.

## Requirements

- Python 3
- Dependencies from `requirements.txt`

## Installation

```bash
python -m venv venv
source venv/bin/activate  # on Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the repository root with at least the following variables:

```ini
# comma-separated list of RSS feed URLs
RSS_FEED_URLS=https://example.com/rss,https://another.example.com/feed

# Mailchimp credentials
MAILCHIMP_API_KEY=your-api-key
MAILCHIMP_SERVER_PREFIX=us1  # e.g. us1, us2
MAILCHIMP_LIST_ID=your-list-id

# email sender details
EMAIL_FROM=you@example.com
EMAIL_FROM_NAME=Your Name
```

If `python-dotenv` is installed (it is included in `requirements.txt`), the scripts will load this file automatically.

You can customize the email template by creating `templates/newsletter.html`. If it is absent, a simple built‑in template is used.

## Usage

1. **Fetch articles**

   ```bash
   python scripts/fetch_rss_feeds.py
   ```

   New articles are written to the `_articles/` directory.

2. **Send the newsletter**

   ```bash
   python scripts/send_newsletter.py
   ```

   The latest articles are loaded and emailed using Mailchimp.

3. **Build the Jekyll site**

   First copy the fetched articles into the Jekyll site's `_posts/` folder. Use
   the helper script or create symlinks:

   ```bash
   # copy files
   ./scripts/sync_articles_to_jekyll.sh
   # or create symlinks instead of copies
   ./scripts/sync_articles_to_jekyll.sh --link
   ```

   Then build the static site:

   ```bash
   jekyll build -s jekyll -d jekyll/_site
   ```

   The generated site will be available under `jekyll/_site/`.

## Roadmap

The repository currently focuses on fetching articles and sending newsletters. Future improvements may include:

- A Jekyll website to publish the collected articles.
- A GitHub Actions workflow to automate fetching and mailing.

## Automation

A scheduled GitHub Actions workflow automatically fetches articles and sends the newsletter. Configure these repository secrets so the workflow can run:
- `RSS_FEED_URLS`
- `MAILCHIMP_API_KEY`
- `MAILCHIMP_SERVER_PREFIX`
- `MAILCHIMP_LIST_ID`
- `EMAIL_FROM`
- `EMAIL_FROM_NAME`


## License

This project is licensed under the [MIT License](LICENSE).
