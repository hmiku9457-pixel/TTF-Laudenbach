#!/usr/bin/env python3
"""Apply the Phase-3 SEO metadata to the TTF-Laudenbach repository.

The script uses only Python's standard library. Run it from the repository
root or call it through the supplied GitHub Actions workflow.
"""

from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

SITE_URL = "https://www.ttf-laudenbach.de"
SITE_NAME = "TTF Laudenbach"
SOCIAL_IMAGE_PATH = "/assets/images/seo/ttf-laudenbach-social.png"
SOCIAL_IMAGE_URL = f"{SITE_URL}{SOCIAL_IMAGE_PATH}"
LOGO_URL = f"{SITE_URL}/assets/images/TTF-Laudenbach_Logo.png"


@dataclass(frozen=True)
class PageMeta:
    title: str
    description: str
    index: bool = True
    canonical_path: str | None = None
    og_type: str = "website"
    sitemap: bool = True


PAGES: dict[str, PageMeta] = {
    "index.html": PageMeta(
        "TTF Laudenbach | Tischtennis in Weikersheim-Laudenbach",
        "TTF Laudenbach – Tischtennis für Kinder, Jugendliche und Erwachsene. Trainingszeiten, Mannschaften, Spielbetrieb, Vereinsleben und Kontakt.",
        canonical_path="/",
    ),
    "404.html": PageMeta(
        "Seite nicht gefunden | TTF Laudenbach",
        "Die aufgerufene Seite wurde nicht gefunden.",
        index=False,
        canonical_path="/404.html",
        sitemap=False,
    ),
    "pages/aktiverSpielbetrieb.html": PageMeta(
        "Training und Spiellokale | TTF Laudenbach",
        "Trainingszeiten, Spiellokale und Informationen zum aktiven Spielbetrieb der Tischtennis-Freunde Laudenbach.",
    ),
    "pages/dokumente.html": PageMeta(
        "Dokumente und Vereinsarchiv | TTF Laudenbach",
        "Dokumente, historische Fotos, Newsletter, Satzung und Mitgliedschaftsunterlagen der TTF Laudenbach.",
    ),
    "pages/index.html": PageMeta(
        "Startseite | TTF Laudenbach",
        "Startseite der Tischtennis-Freunde Laudenbach.",
        index=False,
        canonical_path="/",
        sitemap=False,
    ),
    "pages/links.html": PageMeta(
        "Weiterführende Links | TTF Laudenbach",
        "Weiterführende Links rund um Tischtennis, Verbände, Ergebnisse und den regionalen Sport.",
    ),
    "pages/maintenance.html": PageMeta(
        "Wartungsarbeiten | TTF Laudenbach",
        "Diese Seite befindet sich derzeit in Bearbeitung.",
        index=False,
        sitemap=False,
    ),
    "pages/sponsoren.html": PageMeta(
        "Sponsoren und Partner | TTF Laudenbach",
        "Die Sponsoren und Partner der Tischtennis-Freunde Laudenbach im Überblick.",
    ),
    "pages/startpage.html": PageMeta(
        "Startseite | TTF Laudenbach",
        "Startseite der Tischtennis-Freunde Laudenbach.",
        index=False,
        canonical_path="/",
        sitemap=False,
    ),
    "pages/unserVerein.html": PageMeta(
        "Unser Verein | TTF Laudenbach",
        "Informationen zur Geschichte, den Ansprechpartnern und dem Vereinsleben der Tischtennis-Freunde Laudenbach.",
    ),
    "pages/vereinsmitgliedschaft.html": PageMeta(
        "Mitgliedschaft und Beiträge | TTF Laudenbach",
        "Mitgliedsbeiträge und Beitrittsunterlagen der Tischtennis-Freunde Laudenbach für Jugendliche, Erwachsene und Familien.",
    ),
    "pages/aktiverSpielbetrieb/alleMannschaften.html": PageMeta(
        "Mannschaften im Überblick | TTF Laudenbach",
        "Alle Herren- und Jugendmannschaften der TTF Laudenbach im Überblick.",
    ),
    "pages/aktiverSpielbetrieb/ewigeRangliste.html": PageMeta(
        "Ewige Rangliste | TTF Laudenbach",
        "Die ewige Rangliste der Tischtennis-Freunde Laudenbach mit den historischen Einsätzen und Ergebnissen.",
    ),
    "pages/aktiverSpielbetrieb/herren1.html": PageMeta(
        "1. Herrenmannschaft | TTF Laudenbach",
        "Aufstellung, Tabelle und Spielplan der 1. Herrenmannschaft der TTF Laudenbach.",
    ),
    "pages/aktiverSpielbetrieb/herren2.html": PageMeta(
        "2. Herrenmannschaft | TTF Laudenbach",
        "Aufstellung, Tabelle und Spielplan der 2. Herrenmannschaft der TTF Laudenbach.",
    ),
    "pages/aktiverSpielbetrieb/herren3.html": PageMeta(
        "3. Herrenmannschaft | TTF Laudenbach",
        "Aufstellung, Tabelle und Spielplan der 3. Herrenmannschaft der TTF Laudenbach.",
    ),
    "pages/aktiverSpielbetrieb/herren4.html": PageMeta(
        "4. Herrenmannschaft | TTF Laudenbach",
        "Aufstellung, Tabelle und Spielplan der 4. Herrenmannschaft der TTF Laudenbach.",
    ),
    "pages/aktiverSpielbetrieb/herren5.html": PageMeta(
        "5. Herrenmannschaft | TTF Laudenbach",
        "Aufstellung, Tabelle und Spielplan der 5. Herrenmannschaft der TTF Laudenbach.",
    ),
    "pages/aktiverSpielbetrieb/jugend1.html": PageMeta(
        "1. Jugendmannschaft | TTF Laudenbach",
        "Aufstellung, Tabelle und Spielplan der 1. Jugendmannschaft der TTF Laudenbach.",
    ),
    "pages/aktiverSpielbetrieb/jugend2.html": PageMeta(
        "2. Jugendmannschaft | TTF Laudenbach",
        "Aufstellung, Tabelle und Spielplan der 2. Jugendmannschaft der TTF Laudenbach.",
    ),
    "pages/dokumente/historischeFotos.html": PageMeta(
        "Historische Fotos | TTF Laudenbach",
        "Historische Vereinsfotos und Bilder aus der Geschichte der Tischtennis-Freunde Laudenbach.",
    ),
    "pages/dokumente/newsletter.html": PageMeta(
        "Newsletter-Archiv | TTF Laudenbach",
        "Newsletter und Vereinsinformationen der Tischtennis-Freunde Laudenbach im Archiv.",
    ),
    "pages/footer/datenschutz.html": PageMeta(
        "Datenschutzerklärung | TTF Laudenbach",
        "Datenschutzerklärung der Website der Tischtennis-Freunde Laudenbach.",
        index=False,
        sitemap=False,
    ),
    "pages/footer/impressum.html": PageMeta(
        "Impressum | TTF Laudenbach",
        "Impressum und Anbieterkennzeichnung der Tischtennis-Freunde Laudenbach.",
        index=False,
        sitemap=False,
    ),
    "pages/footer/kontakt.html": PageMeta(
        "Kontakt | TTF Laudenbach",
        "Kontaktmöglichkeiten und Ansprechpartner der Tischtennis-Freunde Laudenbach.",
    ),
    "pages/news/artikel1.html": PageMeta(
        "VierElemente sponsort neue Jacken | TTF Laudenbach",
        "Die Laudenbacher Firma VierElemente stattet die Herren- und Jugendmannschaften der TTF Laudenbach mit neuen Vereinsjacken aus.",
        og_type="article",
    ),
    "pages/news/artikel2.html": PageMeta(
        "49. TTF-Hauptversammlung | TTF Laudenbach",
        "Bericht zur 49. Hauptversammlung und zum 50-jährigen Bestehen der Tischtennis-Freunde Laudenbach.",
        og_type="article",
    ),
}

REMOVE_PATTERNS = [
    re.compile(r"\s*<title\b[^>]*>.*?</title>\s*", re.IGNORECASE | re.DOTALL),
    re.compile(r"\s*<meta\b[^>]*\bname=[\"']description[\"'][^>]*>\s*", re.IGNORECASE),
    re.compile(r"\s*<meta\b[^>]*\bname=[\"']robots[\"'][^>]*>\s*", re.IGNORECASE),
    re.compile(r"\s*<link\b[^>]*\brel=[\"']canonical[\"'][^>]*>\s*", re.IGNORECASE),
    re.compile(r"\s*<meta\b[^>]*\bproperty=[\"']og:[^\"']+[\"'][^>]*>\s*", re.IGNORECASE),
    re.compile(r"\s*<meta\b[^>]*\bname=[\"']twitter:[^\"']+[\"'][^>]*>\s*", re.IGNORECASE),
    re.compile(
        r"\s*<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*\bdata-seo=[\"']ttf-phase3[\"'][^>]*>.*?</script>\s*",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"\s*<!--\s*SEO: TTF Phase 3.*?SEO: Ende TTF Phase 3\s*-->\s*", re.IGNORECASE | re.DOTALL),
]


def escape_attr(value: str) -> str:
    return html.escape(value, quote=True)


def canonical_url(relative_path: str, meta: PageMeta) -> str:
    path = meta.canonical_path
    if path is None:
        path = "/" + quote(relative_path, safe="/.-_~")
    if not path.startswith("/"):
        path = "/" + path
    return SITE_URL + path


def organization_json_ld() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "SportsOrganization",
        "@id": f"{SITE_URL}/#organization",
        "name": "Tischtennis-Freunde Laudenbach",
        "alternateName": "TTF Laudenbach",
        "url": f"{SITE_URL}/",
        "logo": LOGO_URL,
        "image": SOCIAL_IMAGE_URL,
        "description": PAGES["index.html"].description,
        "sport": "Tischtennis",
        "areaServed": {
            "@type": "AdministrativeArea",
            "name": "Weikersheim-Laudenbach",
        },
        "location": [
            {
                "@type": "SportsActivityLocation",
                "name": "Großsporthalle Weikersheim",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Laudenbacher Straße 22",
                    "postalCode": "97990",
                    "addressLocality": "Weikersheim",
                    "addressCountry": "DE",
                },
            },
            {
                "@type": "SportsActivityLocation",
                "name": "Zehntscheune Laudenbach",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Schlössle 9",
                    "postalCode": "97990",
                    "addressLocality": "Weikersheim-Laudenbach",
                    "addressCountry": "DE",
                },
            },
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_block(relative_path: str, meta: PageMeta) -> str:
    url = canonical_url(relative_path, meta)
    robots = "index, follow, max-image-preview:large" if meta.index else "noindex, follow"
    lines = [
        "\t\t<!-- SEO: TTF Phase 3 -->",
        f"\t\t<title>{html.escape(meta.title)}</title>",
        f'\t\t<meta name="description" content="{escape_attr(meta.description)}">',
        f'\t\t<meta name="robots" content="{robots}">',
        f'\t\t<link rel="canonical" href="{escape_attr(url)}">',
        "",
        '\t\t<meta property="og:locale" content="de_DE">',
        f'\t\t<meta property="og:type" content="{meta.og_type}">',
        f'\t\t<meta property="og:site_name" content="{SITE_NAME}">',
        f'\t\t<meta property="og:title" content="{escape_attr(meta.title)}">',
        f'\t\t<meta property="og:description" content="{escape_attr(meta.description)}">',
        f'\t\t<meta property="og:url" content="{escape_attr(url)}">',
        f'\t\t<meta property="og:image" content="{SOCIAL_IMAGE_URL}">',
        '\t\t<meta property="og:image:width" content="1200">',
        '\t\t<meta property="og:image:height" content="630">',
        '\t\t<meta property="og:image:type" content="image/png">',
        '\t\t<meta property="og:image:alt" content="Logo der Tischtennis-Freunde Laudenbach">',
        "",
        '\t\t<meta name="twitter:card" content="summary_large_image">',
        f'\t\t<meta name="twitter:title" content="{escape_attr(meta.title)}">',
        f'\t\t<meta name="twitter:description" content="{escape_attr(meta.description)}">',
        f'\t\t<meta name="twitter:image" content="{SOCIAL_IMAGE_URL}">',
        '\t\t<meta name="twitter:image:alt" content="Logo der Tischtennis-Freunde Laudenbach">',
    ]
    if relative_path == "index.html":
        lines.extend(
            [
                "",
                '\t\t<script type="application/ld+json" data-seo="ttf-phase3">',
                *["\t\t" + line for line in organization_json_ld().splitlines()],
                "\t\t</script>",
            ]
        )
    lines.extend(["\t\t<!-- SEO: Ende TTF Phase 3 -->", ""])
    return "\n".join(lines)


def ensure_viewport(source: str) -> str:
    if re.search(r"<meta\b[^>]*\bname=[\"']viewport[\"']", source, re.IGNORECASE):
        return source
    charset_match = re.search(r"<meta\b[^>]*\bcharset=[^>]+>", source, re.IGNORECASE)
    viewport = '\n\t\t<meta name="viewport" content="width=device-width, initial-scale=1.0">'
    if charset_match:
        return source[: charset_match.end()] + viewport + source[charset_match.end() :]
    head_match = re.search(r"<head\b[^>]*>", source, re.IGNORECASE)
    if not head_match:
        raise ValueError("Kein <head>-Element gefunden")
    return source[: head_match.end()] + viewport + source[head_match.end() :]


def apply_to_html(source: str, relative_path: str, meta: PageMeta) -> str:
    updated = source
    for pattern in REMOVE_PATTERNS:
        updated = pattern.sub("\n", updated)
    updated = ensure_viewport(updated)

    head_end = re.search(r"</head\s*>", updated, re.IGNORECASE)
    if not head_end:
        raise ValueError("Kein schließendes </head>-Element gefunden")

    block = build_block(relative_path, meta)
    before_head_end = updated[: head_end.start()].rstrip()
    after_head_end = updated[head_end.start() :].lstrip("\r\n")
    updated = before_head_end + "\n\n" + block + after_head_end
    updated = re.sub(r"\n{4,}", "\n\n\n", updated)
    if source.endswith("\n") and not updated.endswith("\n"):
        updated += "\n"
    return updated


def find_repo_root(start: Path) -> Path:
    candidates = [start.resolve(), *start.resolve().parents]
    for candidate in candidates:
        if (candidate / "CNAME").exists() and (candidate / "index.html").exists():
            return candidate
    script_root = Path(__file__).resolve().parents[1]
    if (script_root / "CNAME").exists() and (script_root / "index.html").exists():
        return script_root
    raise FileNotFoundError(
        "Repository-Wurzel nicht gefunden. Starte das Skript im TTF-Laudenbach-Repository."
    )


def write_sitemap(root: Path) -> None:
    urls = []
    for relative_path, meta in PAGES.items():
        file_path = root / relative_path
        if meta.index and meta.sitemap and file_path.exists():
            urls.append(canonical_url(relative_path, meta))

    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in sorted(set(urls), key=lambda item: (item != f"{SITE_URL}/", item)):
        body.extend(["\t<url>", f"\t\t<loc>{html.escape(url)}</loc>", "\t</url>"])
    body.append("</urlset>")
    (root / "sitemap.xml").write_text("\n".join(body) + "\n", encoding="utf-8")


def write_robots(root: Path) -> None:
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    (root / "robots.txt").write_text(content, encoding="utf-8")


def existing_page_paths(root: Path) -> Iterable[str]:
    for path in sorted(root.rglob("*.html")):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("components/"):
            continue
        yield relative


def main() -> int:
    try:
        root = find_repo_root(Path.cwd())
    except FileNotFoundError as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1

    changed = 0
    missing = []
    unmanaged = []

    existing = set(existing_page_paths(root))
    for relative_path in sorted(existing):
        meta = PAGES.get(relative_path)
        if meta is None:
            unmanaged.append(relative_path)
            continue
        path = root / relative_path
        source = path.read_text(encoding="utf-8")
        try:
            updated = apply_to_html(source, relative_path, meta)
        except ValueError as error:
            print(f"FEHLER in {relative_path}: {error}", file=sys.stderr)
            return 1
        if updated != source:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"Aktualisiert: {relative_path}")

    for relative_path in sorted(PAGES):
        if not (root / relative_path).exists():
            missing.append(relative_path)

    write_sitemap(root)
    write_robots(root)

    print(f"\nSEO aktualisiert. Geänderte HTML-Dateien: {changed}")
    print("Erzeugt/aktualisiert: sitemap.xml, robots.txt")
    if missing:
        print("Hinweis – konfigurierte, aber nicht vorhandene Dateien:")
        for path in missing:
            print(f"  - {path}")
    if unmanaged:
        print("WARNUNG – HTML-Dateien ohne individuelle SEO-Konfiguration:")
        for path in unmanaged:
            print(f"  - {path}")
        print("Diese Dateien wurden absichtlich nicht automatisch verändert.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
