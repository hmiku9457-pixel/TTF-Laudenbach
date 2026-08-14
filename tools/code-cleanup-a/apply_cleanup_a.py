#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HTTP = ROOT / "assets/js/core/http.js"
LINKS = ROOT / "assets/js/features/links.js"
NEWS_SLIDER = ROOT / "assets/css/components/news-slider.css"
GALLERY = ROOT / "assets/css/components/gallery.css"
CONFIG = ROOT / "assets/python/config.py"
GENERATE_NEWS = ROOT / "assets/python/generate_news.py"


def read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Datei fehlt: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        if text.count(old) != 1:
            raise RuntimeError(f"{label}: erwarteter Abschnitt ist nicht eindeutig.")
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"{label}: weder alter noch bereits bereinigter Abschnitt gefunden.")


def cleanup_http() -> None:
    text = read(HTTP)
    old = """export async function fetchText(url, options = {}) {
    const response = await fetch(url, options);

    if (!response.ok) {
        throw new Error(
            `HTTP ${response.status} (${response.statusText || "Unbekannter Fehler"}) bei ${url}`
        );
    }

    return response.text();
}

"""
    if old in text:
        text = text.replace(old, "", 1)
    elif "export async function fetchText" in text:
        raise RuntimeError("http.js: fetchText-Struktur weicht vom erwarteten Stand ab.")

    if "export async function fetchText" in text:
        raise RuntimeError("http.js: fetchText wurde nicht vollständig entfernt.")
    if "export async function fetchJson" not in text:
        raise RuntimeError("http.js: fetchJson fehlt unerwartet.")
    write(HTTP, text)


def cleanup_news_slider() -> None:
    text = read(NEWS_SLIDER)

    old_link_rules = """.news-slide a {
    width: fit-content;
    margin-top: auto;
    padding: 8px 12px;
    border-radius: var(--space-m);
    background: var(--accent);
    color: var(--text-on-newsSlide);
    text-decoration: none;
}

.news-slide a:hover {
    background: var(--accent-hover);
}
"""
    if old_link_rules in text:
        text = text.replace(old_link_rules, "", 1)
    elif ".news-slide a {" in text or ".news-slide a:hover" in text:
        raise RuntimeError("news-slider.css: alte Link-Regeln weichen vom erwarteten Stand ab.")

    old_selector = ".news-slider--has-footer .news-slide,\n.news-slider--controlled .news-slide {"
    new_selector = ".news-slider--has-footer .news-slide {"

    occurrences = text.count(old_selector)
    if occurrences:
        if occurrences != 3:
            raise RuntimeError(
                f"news-slider.css: kombinierter Padding-Selektor {occurrences}x statt 3x gefunden."
            )
        text = text.replace(old_selector, new_selector)
    elif text.count(new_selector) < 3:
        raise RuntimeError("news-slider.css: bereits bereinigte Footer-Selektoren fehlen.")

    if ".news-slide a {" in text or ".news-slide a:hover" in text:
        raise RuntimeError("news-slider.css: tote Slide-Link-Regeln sind noch vorhanden.")
    if old_selector in text:
        raise RuntimeError("news-slider.css: redundanter Padding-Selektor ist noch vorhanden.")
    if ".news-slider--controlled .news-slide {" not in text:
        raise RuntimeError("news-slider.css: notwendige --controlled-Pointer-Regel fehlt.")

    write(NEWS_SLIDER, text)


def cleanup_gallery() -> None:
    text = read(GALLERY)
    old = """.images-gallery h3 {
    margin-bottom: var(--space-l);
}

"""
    if old in text:
        text = text.replace(old, "", 1)
    elif ".images-gallery h3" in text:
        raise RuntimeError("gallery.css: alte h3-Regel weicht vom erwarteten Stand ab.")

    if ".images-gallery h3" in text:
        raise RuntimeError("gallery.css: tote h3-Regel ist noch vorhanden.")
    write(GALLERY, text)


def cleanup_config() -> None:
    text = read(CONFIG)
    old_line = '                "bild": "./assets/images/TTF-Laudenbach_Logo.png",\n'
    count = text.count(old_line)

    if count:
        if count != 4:
            raise RuntimeError(f"config.py: Sponsor-bild-Feld {count}x statt 4x gefunden.")
        text = text.replace(old_line, "")
    elif '"bild": "./assets/images/TTF-Laudenbach_Logo.png"' in text:
        raise RuntimeError("config.py: Sponsor-bild-Felder haben unerwartete Formatierung.")

    if '"bild": "./assets/images/TTF-Laudenbach_Logo.png"' in text:
        raise RuntimeError("config.py: Sponsor-bild-Felder sind noch vorhanden.")
    write(CONFIG, text)


def cleanup_links() -> None:
    text = read(LINKS)

    imports = """import { fetchJson } from "../core/http.js";
import { showContainerStatus } from "../core/status.js";
import { getSafeHttpUrl } from "../utils/safe-url.js";
"""
    constant = """
const SPONSOR_SLOTS = ["sponsor1", "sponsor2", "sponsor3", "sponsor4"];
"""

    if "const SPONSOR_SLOTS =" not in text:
        if imports not in text:
            raise RuntimeError("links.js: Importblock wurde nicht gefunden.")
        text = text.replace(imports, imports + constant, 1)

    local = '        const sponsorSlots = ["sponsor1", "sponsor2", "sponsor3", "sponsor4"];\n'
    if local in text:
        text = text.replace(local, "", 1)
    elif "const sponsorSlots =" in text:
        raise RuntimeError("links.js: lokale sponsorSlots-Definition hat unerwartete Form.")

    if "sponsorSlots.includes(link.id)" in text:
        text = text.replace(
            "sponsorSlots.includes(link.id)",
            "SPONSOR_SLOTS.includes(link.id)",
            1,
        )

    old_error = '    ["sponsor1", "sponsor2", "sponsor3", "sponsor4"].forEach(slot => {'
    new_error = "    SPONSOR_SLOTS.forEach(slot => {"
    if old_error in text:
        text = text.replace(old_error, new_error, 1)
    elif new_error not in text:
        raise RuntimeError("links.js: Sponsor-Fehlerbehandlung wurde nicht gefunden.")

    if text.count("const SPONSOR_SLOTS =") != 1:
        raise RuntimeError("links.js: SPONSOR_SLOTS muss genau einmal definiert sein.")
    if "sponsorSlots" in text:
        raise RuntimeError("links.js: alte sponsorSlots-Variable ist noch vorhanden.")
    if "SPONSOR_SLOTS.includes(link.id)" not in text:
        raise RuntimeError("links.js: zentrale Sponsor-Slot-Liste wird beim Laden nicht verwendet.")
    if "SPONSOR_SLOTS.forEach(slot => {" not in text:
        raise RuntimeError("links.js: zentrale Sponsor-Slot-Liste wird im Fehlerfall nicht verwendet.")

    write(LINKS, text)


def cleanup_news_generator() -> None:
    text = read(GENERATE_NEWS)
    old = '        if GENERATED_MARKER in text or path.name in {"artikel1.html", "artikel2.html"}:\n'
    new = '        if GENERATED_MARKER in text:\n'
    text = replace_once(
        text,
        old,
        new,
        "generate_news.py: historische artikel1/artikel2-Sonderbehandlung",
    )

    if "artikel1.html" in text or "artikel2.html" in text:
        raise RuntimeError(
            "generate_news.py: historische artikel1/artikel2-Sonderbehandlung ist noch vorhanden."
        )
    write(GENERATE_NEWS, text)


def validate_css(path: Path) -> None:
    text = read(path)
    if text.count("{") != text.count("}"):
        raise RuntimeError(f"{path.relative_to(ROOT)}: geschweifte Klammern sind unausgeglichen.")


def main() -> None:
    cleanup_http()
    cleanup_news_slider()
    cleanup_gallery()
    cleanup_config()
    cleanup_links()
    cleanup_news_generator()
    validate_css(NEWS_SLIDER)
    validate_css(GALLERY)
    print("Code-Cleanup A erfolgreich angewendet.")


if __name__ == "__main__":
    main()
