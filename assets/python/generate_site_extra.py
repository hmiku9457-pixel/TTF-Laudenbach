#!/usr/bin/env python3
"""Render weitere strukturierte Vereinsinformationen in das Pages-Artefakt."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
from generate_site import ROOT, SOURCE, load, text, seq, local, rich, table, button, render_page, web
from generate_news import render_sections, render_divider_block, render_spacer_block


def pdf(value):
    return local(value, "/pages/dokumente/", {".pdf"})


def pairs(items):
    names = [text(n) for n in seq(items)]
    return [names[i:i+2] + ([""] if i == len(names)-1 else []) for i in range(0, len(names), 2)]



def page_sections(blocks, source):
    parts = []
    for i, block in enumerate(seq(blocks), 1):
        if not isinstance(block, dict):
            raise ValueError(f"{source.name}: Block {i} muss ein Objekt sein")
        kind = block.get("type")
        if kind in ("text", "two_columns", "event"):
            parts.append(render_sections([block], source))
        elif kind == "heading":
            parts.append(f'<h2 class="news-block">{text(block["title"])}</h2>')
        elif kind == "three_columns":
            columns = "".join(f'<div class="news-block__column">{rich(block[k], source.stem)}</div>' for k in ("left", "middle", "right"))
            parts.append(f'<section class="news-block news-block--columns news-block--three">{columns}</section>')
        elif kind == "gallery":
            figures = []
            for item in seq(block.get("images")):
                src = local(item["src"], "/assets/images/site/", {".jpg", ".jpeg", ".png", ".webp"})
                figures.append(f'<img src="{src}" alt="{text(item["alt"])}" loading="lazy"/>')
            if figures:
                parts.append(f'<div class="news-block cms-image-row">{"".join(figures)}</div>')
        elif kind == "divider":
            parts.append(render_divider_block())
        elif kind == "spacer":
            parts.append(render_spacer_block(block, source, i))
        elif kind == "image":
            src = local(block["src"], "/assets/images/site/", {".jpg", ".jpeg", ".png", ".webp"})
            caption = f'<figcaption class="u-text-center">{text(block["caption"])}</figcaption>' if block.get("caption") else ""
            parts.append(f'<figure class="news-block news-rich-image"><img src="{src}" alt="{text(block["alt"])}" loading="lazy"/>{caption}</figure>')
        elif kind in ("button", "download"):
            href = web(block["url"]) if kind == "button" else pdf(block["path"])
            parts.append(f'<div class="news-block grid-button">{button(block["label"], href)}</div>')
        elif kind == "notice":
            body = rich(block["body"], source.stem)
            parts.append(f'<section class="news-block news-event"><h2 class="news-event__title">{text(block["title"])}</h2>{body}</section>')
        else:
            raise ValueError(f"{source.name}: Unbekannter Block {kind!r}")
    return "\n".join(parts)


def build(output):
    club, membership, documents, newsletter, settings = [load(n) for n in ("club", "membership", "documents", "newsletter", "settings")]
    values = {
        "club_intro": rich(club["intro"], "club"),
        "board": table("Ausschuss", [[text(r["role"]), "".join(f"<p>{text(n)}</p>" for n in seq(r.get("names")))] for r in seq(club.get("board"))]),
        "honor": table("Ehrenvorsitzender & Ehrenmitglieder", [[text(r["role"]), text(r["name"])] for r in seq(club.get("honor"))], ("Rolle", "Name"), "table--emphasis-first-column", True),
        "founders": table("Gründungsmitglieder 1969", pairs(club.get("founders"))),
        "members": table("Mitglieder 1975", pairs(club.get("members")), row_header=True),
        "history": table("Vorstandsverlauf", [[text(r[k]) for k in ("period", "chair", "deputy")] for r in seq(club.get("history"))], ("Amtszeit", "Vorsitzender / Abteilungsleiter", "Stellvertretender Vorsitzender / Stellv. Abteilungsleiter"), row_header=True),
        "membership_intro": rich(membership["intro"], "membership"),
        "extra_documents": "".join(button(r["title"], pdf(r["path"])) for r in seq(documents.get("extra"))),
        "subtitle": text(settings["subtitle"]),
        "newsletter_title": text(newsletter["title"]),
        "newsletter_sections": page_sections(newsletter.get("sections"), SOURCE / "newsletter.json")
    }
    fee_rows = []
    for r in seq(membership.get("fees")):
        try:
            n = Decimal(str(r["amount"]))
            if not n.is_finite() or n < 0 or n != n.quantize(Decimal(".01")):
                raise ValueError("Mitgliedsbeitrag muss nichtnegativ sein und maximal zwei Dezimalstellen haben")
        except InvalidOperation as exc:
            raise ValueError("Ungültiger Mitgliedsbeitrag") from exc
        amount = f"{n:.2f}".replace(".", ",") if n != n.to_integral_value() else f"{n:.0f}"
        category = text(r["category"])
        if r.get("note"):
            category = f'<p>{category}</p><p>{text(r["note"])}</p>'
        fee_rows.append([category, amount + "€"])
    values["fees"] = table("Mitgliedsbeiträge pro Jahr", fee_rows, ("Mitgliedschaft", "Jahresbeitrag"))
    stat, join = pdf(documents["statutes"]), pdf(documents["join"])
    seen = set()
    for target in ("pages/unserVerein.html", "pages/vereinsmitgliedschaft.html", "pages/dokumente.html", "pages/dokumente/newsletter.html", "components/header.html"):
        seen |= render_page(output, target, values)
        p = output / target
        page = p.read_text(encoding="utf-8").replace("{{CMS_STATUTES}}", stat).replace("{{CMS_JOIN}}", join)
        if "{{CMS_" in page:
            raise ValueError(f"Nicht ersetzter Dokumentenlink: {target}")
        p.write_text(page, encoding="utf-8")
    if set(values)-seen:
        raise ValueError(f"Nicht verwendete CMS-Bausteine: {set(values)-seen}")
    from generate_site_layout import apply_layouts
    apply_layouts(output)
    from generate_site_legal import build as build_legal
    build_legal(output)
    print("CMS: Verein, Mitgliedschaft, Dokumente, Newsletter, Header und Seitenbaukasten erzeugt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == ROOT or not (args.output / "assets/data").is_dir():
        raise SystemExit("Separates, vorbereitetes Website-Artefakt erforderlich.")
    build(args.output.resolve())
