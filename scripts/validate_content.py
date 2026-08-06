#!/usr/bin/env python3
"""Validate posts, PDF notes, and assets before Jekyll builds the site."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = ROOT / "assets"
POSTS_ROOT = ROOT / "_posts"
CATEGORIES_FILE = ROOT / "_data" / "categories.yml"
MAX_SINGLE_FILE_BYTES = 95 * 1024 * 1024
MAX_PUBLISHED_ASSETS_BYTES = 200 * 1024 * 1024
POST_NAME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}-.+\.(?:md|markdown)$", re.IGNORECASE
)


def format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def is_published_asset(path: Path) -> bool:
    relative = path.relative_to(ASSETS_ROOT)
    return relative.parts[0] != "music" and relative.as_posix() != "js/music-player.js"


def category_keys() -> set[str]:
    if not CATEGORIES_FILE.exists():
        return set()
    keys = set()
    for raw in CATEGORIES_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- key:"):
            keys.add(line.split(":", 1)[1].strip().strip('"\''))
    return keys


def validate_posts(errors: list[str]) -> None:
    if not POSTS_ROOT.exists():
        return
    for path in sorted(POSTS_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.casefold() not in {".md", ".markdown"}:
            continue
        if not POST_NAME_PATTERN.match(path.name):
            errors.append(f"Blog filename must be YYYY-MM-DD-slug.md: {path.relative_to(ROOT)}")
        try:
            text = path.read_text(encoding="utf-8").lstrip("\ufeff")
        except UnicodeDecodeError:
            errors.append(f"Blog file is not UTF-8: {path.relative_to(ROOT)}")
            continue
        if not (text.startswith("---\n") or text.startswith("---\r\n")):
            errors.append(f"Blog front matter is missing: {path.relative_to(ROOT)}")


def validate_notes(errors: list[str]) -> None:
    known_categories = category_keys()
    seen: dict[tuple[str, str], Path] = {}
    for notes_root in (ASSETS_ROOT / "notes", ASSETS_ROOT / "pdf"):
        if not notes_root.exists():
            continue
        for path in sorted(notes_root.rglob("*.pdf")):
            with path.open("rb") as pdf_file:
                if pdf_file.read(5) != b"%PDF-":
                    errors.append(f"Invalid PDF file: {path.relative_to(ROOT)}")
                    continue
            relative = path.relative_to(notes_root)
            if len(relative.parts) < 2:
                errors.append(f"PDF must be inside a category folder: {path.relative_to(ROOT)}")
                continue
            category = relative.parts[0]
            if category not in known_categories:
                errors.append(f"Unknown PDF category '{category}': {path.relative_to(ROOT)}")
            slug = Path(*relative.parts[1:]).with_suffix("").as_posix().casefold()
            key = (category.casefold(), slug)
            previous = seen.get(key)
            if previous:
                errors.append(
                    "Duplicate PDF note: "
                    f"{previous.relative_to(ROOT)} and {path.relative_to(ROOT)}"
                )
            else:
                seen[key] = path


def published_assets() -> list[Path]:
    if not ASSETS_ROOT.exists():
        return []
    return [
        path
        for path in ASSETS_ROOT.rglob("*")
        if path.is_file() and is_published_asset(path)
    ]


def validate_assets(errors: list[str]) -> int:
    files = published_assets()
    total_size = sum(path.stat().st_size for path in files)
    if total_size > MAX_PUBLISHED_ASSETS_BYTES:
        errors.append(
            f"Published assets are too large: {format_size(total_size)} "
            f"(limit {format_size(MAX_PUBLISHED_ASSETS_BYTES)})."
        )
    for path in files:
        if path.stat().st_size > MAX_SINGLE_FILE_BYTES:
            errors.append(
                f"File exceeds the safe upload limit: {path.relative_to(ROOT)} "
                f"({format_size(path.stat().st_size)})"
            )
    return total_size


def main() -> int:
    errors: list[str] = []
    validate_posts(errors)
    validate_notes(errors)
    total_size = validate_assets(errors)
    if errors:
        print("Content validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Content validation passed. Published assets: {format_size(total_size)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
