import os
import feedparser
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # fallback if python-dotenv isn't installed
    load_dotenv = None


def slugify(value: str) -> str:
    """Simple slugify function for filenames."""
    return "-".join(
        filter(None, [
            ''.join(c.lower() if c.isalnum() else '-' for c in value).strip('-')
        ])
    )


def load_env():
    if load_dotenv:
        load_dotenv()


def get_feed_urls() -> list[str]:
    urls = os.getenv('RSS_FEED_URLS', '')
    return [u.strip() for u in urls.split(',') if u.strip()]


def fetch_and_save_articles(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    feed_urls = get_feed_urls()
    if not feed_urls:
        print('No RSS_FEED_URLS specified. Exiting.')
        return
    for url in feed_urls:
        print(f'Fetching feed: {url}')
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', 'Untitled')
            published = entry.get('published', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')
            if published:
                try:
                    published_date = datetime(*entry.published_parsed[:6])
                except Exception:
                    published_date = datetime.utcnow()
            else:
                published_date = datetime.utcnow()
            slug = slugify(title) or slugify(link) or published_date.strftime('%Y%m%d%H%M%S')
            filename = output_dir / f'{slug}.md'
            if filename.exists():
                continue
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('---\n')
                f.write(f'title: "{title}"\n')
                f.write(f'date: {published_date.isoformat()}\n')
                f.write(f'link: {link}\n')
                f.write(f'source: {feed.feed.get("title", url)}\n')
                f.write('---\n\n')
                f.write(summary)
            print(f'Wrote {filename}')


def main():
    load_env()
    output_dir = Path('_articles')
    fetch_and_save_articles(output_dir)


if __name__ == '__main__':
    main()
