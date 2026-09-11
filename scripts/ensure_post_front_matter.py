#!/usr/bin/env python3
"""Prepare freely named blog uploads, or add front matter in legacy local mode."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml


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
    parser.add_argument("--site-output-dir", help="Prepare a separate Jekyll source tree without editing uploaded files")
    args = parser.parse_args()

    if args.site_output_dir:
        try:
            prepare_site(Path.cwd(), Path(args.site_output_dir), args.dry_run)
        except (ValueError, OSError, subprocess.CalledProcessError, yaml.YAMLError) as error:
            print(f"Blog preparation failed: {error}", file=sys.stderr)
            return 1
        return 0

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


def first_commit_date(root: Path, path: Path) -> str:
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%aI", "--", path.relative_to(root).as_posix()],
        cwd=root, capture_output=True, text=True, check=True,
    )
    dates = result.stdout.strip().splitlines()
    if not dates:
        raise ValueError(f"{path.name}: no Git history; commit the file or specify date in front matter")
    return datetime.fromisoformat(dates[-1]).astimezone(
        timezone(timedelta(hours=8))
    ).strftime("%Y-%m-%d %H:%M:%S +0800")


def prepare_site(root: Path, output: Path, dry_run: bool = False) -> None:
    root, output = root.resolve(), output.resolve()
    if output == root or output in root.parents or output.exists():
        raise ValueError("Output must be a new directory separate from the source")
    prepared = []
    destinations = {}
    for path in sorted((root / "_posts").rglob("*")):
        if not path.is_file() or path.suffix.casefold() not in POST_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8-sig")
        metadata = {}
        body = text
        if has_front_matter(text):
            match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
            if not match:
                raise ValueError(f"{path.name}: front matter is not closed")
            metadata = yaml.safe_load(match.group(1)) or {}
            if not isinstance(metadata, dict):
                raise ValueError(f"{path.name}: front matter must be a mapping")
            body = text[match.end():]
        complete_legacy = bool(DATE_SLUG_PATTERN.match(path.stem)) and has_front_matter(text) and all(
            metadata.get(field) for field in ("layout", "title", "date")
        )
        prefix, slug = split_date_and_slug(path)
        if not metadata.get("date"):
            metadata["date"] = f"{prefix} 00:00:00 +0800" if prefix else first_commit_date(root, path)
        date_text = str(metadata["date"])
        try:
            publication_day = datetime.fromisoformat(date_text).date().isoformat()
        except ValueError as error:
            raise ValueError(f"{path.name}: invalid date {date_text!r}") from error
        metadata.setdefault("layout", "post")
        if not metadata.get("title"):
            metadata["title"] = title_from_heading(body) or slug
        # Explicit slug decouples the URL from the displayed title.
        metadata.setdefault("slug", slug)
        metadata.setdefault("cover", f"/assets/images/blog/{slug}.jpg")
        relative = path.relative_to(root / "_posts")
        target = relative.with_name(f"{prefix or publication_day}-{slug}{path.suffix.lower()}")
        key = target.as_posix().casefold()
        if key in destinations:
            raise ValueError(f"Conflicting blog filenames: {destinations[key]} and {relative}")
        destinations[key] = relative
        # Preserve the metadata and body of already complete legacy posts.
        rendered = text if complete_legacy else "---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False) + "---\n" + body
        prepared.append((relative, target, rendered))
    if dry_run:
        for source, target, _ in prepared:
            print(f"Would prepare: {source} -> {target}")
        return
    shutil.copytree(root, output, ignore=shutil.ignore_patterns(".git", "_site", ".jekyll-cache", "vendor", "__pycache__", output.name))
    # All conflicts are checked before touching the build copy.
    for source, _, _ in prepared:
        (output / "_posts" / source).unlink()
    for _, target, rendered in prepared:
        destination = output / "_posts" / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(f"Prepared {len(prepared)} blog posts in {output}")


if __name__ == "__main__":
    raise SystemExit(main())
