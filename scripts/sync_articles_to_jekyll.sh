#!/bin/bash
# Copy or symlink articles from _articles/ to jekyll/_posts/
# Usage: ./scripts/sync_articles_to_jekyll.sh [--link]
# Without --link, files are copied. With --link, symlinks are created.
set -euo pipefail

SOURCE_DIR="_articles"
TARGET_DIR="jekyll/_posts"
mkdir -p "$TARGET_DIR"

for f in "$SOURCE_DIR"/*.md; do
    [ -e "$f" ] || continue
    filename="$(basename "$f" .md)"
    # extract date from front matter and format as YYYY-MM-DD
    date_line=$(awk -F': ' '/^date:/ {print $2; exit}' "$f")
    if [ -n "$date_line" ]; then
        date_prefix=$(echo "$date_line" | cut -c1-10)
    else
        date_prefix=$(date +%Y-%m-%d)
    fi
    dest="$TARGET_DIR/${date_prefix}-${filename}.md"
    if [ "${1-}" = "--link" ]; then
        ln -sf "../../$f" "$dest"
    else
        cp "$f" "$dest"
    fi
    echo "Synced $f -> $dest"
done
