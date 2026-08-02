#!/usr/bin/env python3
"""Validate the Phase-3 SEO output without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

from apply_phase3_seo import PAGES, SITE_URL, canonical_url, find_repo_root


def count(pattern: str, source: str) -> int:
    return len(re.findall(pattern, source, re.IGNORECASE | re.DOTALL))


def main() -> int:
    try:
        root = find_repo_root(Path.cwd())
    except FileNotFoundError as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1

    errors: list[str] = []

    for relative_path, meta in sorted(PAGES.items()):
        path = root / relative_path
        if not path.exists():
            continue
        source = path.read_text(encoding="utf-8")
        expected_url = canonical_url(relative_path, meta)

        checks = {
            "title": count(r"<title\b[^>]*>.*?</title>", source),
            "description": count(r"<meta\b[^>]*name=[\"']description[\"']", source),
            "robots": count(r"<meta\b[^>]*name=[\"']robots[\"']", source),
            "canonical": count(r"<link\b[^>]*rel=[\"']canonical[\"']", source),
            "og:title": count(r"<meta\b[^>]*property=[\"']og:title[\"']", source),
            "og:image": count(r"<meta\b[^>]*property=[\"']og:image[\"']", source),
            "twitter:card": count(r"<meta\b[^>]*name=[\"']twitter:card[\"']", source),
        }
        for name, actual in checks.items():
            if actual != 1:
                errors.append(f"{relative_path}: {name} kommt {actual}x vor (erwartet: 1x)")

        if f'href="{expected_url}"' not in source:
            errors.append(f"{relative_path}: Canonical-URL fehlt oder ist falsch")

        expected_robots = "index, follow, max-image-preview:large" if meta.index else "noindex, follow"
        if f'content="{expected_robots}"' not in source:
            errors.append(f"{relative_path}: robots-Inhalt ist falsch")

    index = root / "index.html"
    if index.exists():
        source = index.read_text(encoding="utf-8")
        match = re.search(
            r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*data-seo=["\']ttf-phase3["\'][^>]*>(.*?)</script>',
            source,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            errors.append("index.html: SportsOrganization-JSON-LD fehlt")
        else:
            try:
                data = json.loads(match.group(1))
                if data.get("@type") != "SportsOrganization":
                    errors.append("index.html: JSON-LD hat nicht @type SportsOrganization")
            except json.JSONDecodeError as error:
                errors.append(f"index.html: JSON-LD ist ungültig: {error}")

    sitemap = root / "sitemap.xml"
    if not sitemap.exists():
        errors.append("sitemap.xml fehlt")
    else:
        try:
            tree = ElementTree.parse(sitemap)
            namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = {element.text for element in tree.findall("s:url/s:loc", namespace)}
            expected = {
                canonical_url(path, meta)
                for path, meta in PAGES.items()
                if meta.index and meta.sitemap and (root / path).exists()
            }
            if urls != expected:
                errors.append(
                    f"sitemap.xml: URL-Menge weicht ab (gefunden {len(urls)}, erwartet {len(expected)})"
                )
        except ElementTree.ParseError as error:
            errors.append(f"sitemap.xml ist ungültiges XML: {error}")

    robots = root / "robots.txt"
    if not robots.exists():
        errors.append("robots.txt fehlt")
    else:
        content = robots.read_text(encoding="utf-8")
        if f"Sitemap: {SITE_URL}/sitemap.xml" not in content:
            errors.append("robots.txt: Sitemap-Verweis fehlt")

    social = root / "assets/images/seo/ttf-laudenbach-social.png"
    if not social.exists():
        errors.append("Social-Preview-Bild fehlt")

    if errors:
        print("SEO-Prüfung fehlgeschlagen:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SEO-Prüfung erfolgreich.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
