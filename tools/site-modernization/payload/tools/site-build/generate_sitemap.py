#!/usr/bin/env python3
from __future__ import annotations
import argparse
import html
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "sitemap.xml"
BASE_URL = "https://www.ttf-laudenbach.de"
EXCLUDED = {"404.html", "pages/index.html", "pages/startpage.html", "pages/maintenance.html"}
CANONICAL_RE = re.compile(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', re.I)
ROBOTS_RE = re.compile(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)', re.I)


def git_date(path: Path) -> str | None:
    relative = str(path.relative_to(ROOT))
    try:
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "--", relative],
            cwd=ROOT, check=False
        ).returncode != 0
        untracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative],
            cwd=ROOT, check=False, capture_output=True
        ).returncode != 0
        if dirty or untracked:
            return date.today().isoformat()
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", relative],
            cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
        return result or None
    except OSError:
        return None


def page_url(path: Path, text: str) -> str:
    canonical = CANONICAL_RE.search(text)
    if canonical:
        return canonical.group(1).strip()
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return BASE_URL + "/"
    return BASE_URL + "/" + rel


def collect() -> list[tuple[str, str | None]]:
    files = [ROOT / "index.html", *sorted((ROOT / "pages").rglob("*.html"))]
    entries = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXCLUDED:
            continue
        text = path.read_text(encoding="utf-8")
        robots = ROBOTS_RE.search(text)
        if robots and "noindex" in robots.group(1).lower():
            continue
        entries.append((page_url(path, text), git_date(path)))
    entries.sort(key=lambda item: (item[0] != BASE_URL + "/", item[0]))
    return entries


def render() -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, lastmod in collect():
        lines.append("  <url>")
        lines.append(f"    <loc>{html.escape(url)}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build(write: bool) -> int:
    generated = render()
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
    if generated == current:
        print("Sitemap ist aktuell.")
        return 0
    if write:
        OUTPUT.write_text(generated, encoding="utf-8")
        print(f"Sitemap mit {len(collect())} URLs aktualisiert.")
        return 0
    print("sitemap.xml ist nicht aktuell.")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    raise SystemExit(build(args.write))
