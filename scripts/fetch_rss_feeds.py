import os
from pathlib import Path
import feedparser
from dotenv import load_dotenv

load_dotenv()

RSS_FEED_URLS = os.getenv("RSS_FEED_URLS", "").split(',')
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "website/_articles"))


def fetch_and_write():
    if not any(RSS_FEED_URLS) or RSS_FEED_URLS == ['']:
        print("No RSS_FEED_URLS provided in environment.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for url in [u.strip() for u in RSS_FEED_URLS if u.strip()]:
        print(f"Fetching {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "No Title")
            slug = entry.get("id", title).replace('/', '_').replace(' ', '-')
            filename = OUTPUT_DIR / f"{slug}.md"
            date = entry.get("published", "")
            content = entry.get("summary", "")
            md = f"---\ntitle: \"{title}\"\ndate: {date}\n---\n\n{content}\n"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Wrote {filename}")


if __name__ == "__main__":
    fetch_and_write()
