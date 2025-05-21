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
    filename="$(basename "$f")"
    dest="$TARGET_DIR/$filename"
    if [ "${1-}" = "--link" ]; then
        ln -sf "../../$f" "$dest"
    else
        cp "$f" "$dest"
    fi
    echo "Synced $f -> $dest"
done
