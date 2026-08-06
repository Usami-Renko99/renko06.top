#!/usr/bin/env python3
"""Generate _data/notes.json from PDF notes and optional TeX sources."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "_data"
OUT_FILE = DATA_DIR / "notes.json"
CATEGORIES_FILE = DATA_DIR / "categories.yml"
PDF_ROOTS = [ROOT / "assets" / "notes", ROOT / "assets" / "pdf"]
TEX_ROOTS = [ROOT / "assets" / "notes", ROOT / "assets" / "tex"]


def read_categories() -> dict[str, dict[str, str]]:
    categories: dict[str, dict[str, str]] = {}
    current: dict[str, str] = {}
    if not CATEGORIES_FILE.exists():
        return categories
    for raw in CATEGORIES_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-"):
            if current.get("key"):
                categories[current["key"]] = current
            current = {}
            line = line[1:].strip()
        if ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip().strip('"').strip("'")
    if current.get("key"):
        categories[current["key"]] = current
    return categories


def scan_files(roots: list[Path], suffix: str) -> dict[tuple[str, str], Path]:
    found: dict[tuple[str, str], Path] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob(f"*{suffix}")):
            relative = path.relative_to(root)
            if path.is_file() and len(relative.parts) >= 2:
                category = relative.parts[0]
                slug = Path(*relative.parts[1:]).with_suffix("").as_posix()
                found[(category, slug)] = path
    return found


def title_from_slug(slug: str) -> str:
    return " ".join(word.capitalize() for word in Path(slug).name.replace("_", "-").split("-"))


def url_for(path: Path) -> str:
    return "/" + quote(path.relative_to(ROOT).as_posix())


def updated_date(path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except OSError:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


def human_size(path: Path) -> str:
    value = float(path.stat().st_size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    categories = read_categories()
    pdfs = scan_files(PDF_ROOTS, ".pdf")
    texs = scan_files(TEX_ROOTS, ".tex")
    normalized_texs = {
        (category.casefold(), slug.casefold()): path
        for (category, slug), path in texs.items()
    }

    notes = []
    for category, slug in sorted(pdfs):
        pdf = pdfs[(category, slug)]
        tex = texs.get((category, slug)) or normalized_texs.get(
            (category.casefold(), slug.casefold())
        )
        category_title = categories.get(category, {}).get(
            "title", category.replace("-", " ").title()
        )
        notes.append(
            {
                "title": title_from_slug(slug),
                "slug": slug,
                "category": category,
                "category_title": category_title,
                "updated": updated_date(pdf),
                "pdf_url": url_for(pdf),
                "tex_url": url_for(tex) if tex else None,
                "pdf_size": human_size(pdf),
            }
        )

    notes.sort(key=lambda note: (note["category"], note["title"].casefold()))
    OUT_FILE.write_text(
        json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    try:
        display_path = OUT_FILE.relative_to(ROOT)
    except ValueError:
        display_path = OUT_FILE
    print(f"Generated {display_path} with {len(notes)} PDF notes.")


if __name__ == "__main__":
    main()
