#!/usr/bin/env python3
"""Add safe default front matter to blog posts that do not have it."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


POST_EXTENSIONS = {".md", ".markdown"}
DATE_SLUG_PATTERN = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?:-(?P<slug>.+))?$")
H1_PATTERN = re.compile(r"^\s*#\s+(.+?)\s*#*\s*$", re.MULTILINE)


def has_front_matter(text: str) -> bool:
    text = text.lstrip("\ufeff")
    return text.startswith("---\n") or text.startswith("---\r\n")


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def title_from_heading(text: str) -> str | None:
    match = H1_PATTERN.search(text)
    if not match:
        return None
    title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match.group(1).strip())
    return title.strip("`*_ ") or None


def split_date_and_slug(path: Path) -> tuple[str | None, str]:
    match = DATE_SLUG_PATTERN.match(path.stem)
    if not match:
        return None, path.stem
    return match.group("date"), match.group("slug") or path.stem


def humanize_slug(slug: str) -> str:
    words = slug.replace("-", " ").replace("_", " ").strip().split()
    return " ".join(word[:1].upper() + word[1:] for word in words) or "Untitled"


def build_front_matter(path: Path, body: str) -> str:
    date_prefix, slug = split_date_and_slug(path)
    date = (
        f"{date_prefix} 00:00:00 +0800"
        if date_prefix
        else datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S +0800")
    )
    title = title_from_heading(body) or humanize_slug(slug)
    return "\n".join(
        [
            "---",
            "layout: post",
            f"title: {yaml_quote(title)}",
            f"date: {yaml_quote(date)}",
            f"cover: /assets/images/blog/{slug}.jpg",
            'cover_alt: ""',
            'cover_caption: ""',
            "---",
            "",
        ]
    )


def ensure_front_matter(path: Path, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    if has_front_matter(text):
        return False
    body = text.lstrip("\ufeff\r\n")
    if not dry_run:
        newline = "\r\n" if "\r\n" in text else "\n"
        updated = build_front_matter(path, body).replace("\n", newline) + body
        path.write_text(updated, encoding="utf-8", newline="")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--posts-dir", default="_posts")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    posts_dir = Path(args.posts_dir)
    files = (
        sorted(
            path
            for path in posts_dir.rglob("*")
            if path.is_file() and path.suffix.casefold() in POST_EXTENSIONS
        )
        if posts_dir.exists()
        else []
    )
    changed = [path for path in files if ensure_front_matter(path, args.dry_run)]
    action = "Would update" if args.dry_run else "Updated"
    for path in changed:
        print(f"{action}: {path}")
    if not changed:
        print("All post Markdown files already have front matter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
