#!/usr/bin/env python3
"""Verify required pages and internal links in the generated Jekyll site."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
REQUIRED_OUTPUTS = (
    "index.html",
    "about/index.html",
    "blog/index.html",
    "notes/index.html",
    "questions/index.html",
    "feed.xml",
    "CNAME",
    "assets/css/style.css",
)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute = (
            "href"
            if tag in {"a", "link"}
            else "src"
            if tag in {"iframe", "img", "script", "source"}
            else None
        )
        if attribute:
            self.links.extend(value for name, value in attrs if name == attribute and value)


def candidate_paths(url_path: str) -> list[Path]:
    clean = unquote(url_path).lstrip("/")
    if not clean:
        return [SITE_ROOT / "index.html"]
    direct = SITE_ROOT / clean
    candidates = [direct]
    if url_path.endswith("/") or not direct.suffix:
        candidates.extend([direct / "index.html", direct.with_suffix(".html")])
    return candidates


def is_internal_link(link: str) -> bool:
    if link.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return False
    parsed = urlsplit(link)
    return not parsed.scheme and not parsed.netloc


def main() -> int:
    if not SITE_ROOT.is_dir():
        print("Generated site directory is missing: _site", file=sys.stderr)
        return 1

    errors = [
        f"Required generated file is missing: {relative}"
        for relative in REQUIRED_OUTPUTS
        if not (SITE_ROOT / relative).exists()
    ]
    html_files = sorted(SITE_ROOT.rglob("*.html"))
    if not html_files:
        errors.append("No generated HTML files were found.")

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8")
        if "{{" in text or "{%" in text:
            errors.append(f"Unrendered Liquid markup: {html_file.relative_to(SITE_ROOT)}")
        collector = LinkCollector()
        collector.feed(text)
        for link in collector.links:
            if not is_internal_link(link):
                continue
            url_path = urlsplit(link).path
            if url_path and not any(path.exists() for path in candidate_paths(url_path)):
                errors.append(
                    f"Broken internal link in {html_file.relative_to(SITE_ROOT)}: {link}"
                )

    if errors:
        print("Generated site verification failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Generated site verification passed for {len(html_files)} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
