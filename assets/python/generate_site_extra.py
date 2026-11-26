#!/usr/bin/env python3
"""Render weitere strukturierte Vereinsinformationen in das Pages-Artefakt."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
from generate_site import ROOT, SOURCE, load, text, seq, local, rich, table, button, render_page
from generate_news import render_sections


def pdf(value):
    return local(value, "/pages/dokumente/", {".pdf"})


def pairs(items):
    names = [text(n) for n in seq(items)]
    return [names[i:i+2] + ([""] if i == len(names)-1 else []) for i in range(0, len(names), 2)]


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
        "newsletter_sections": render_sections(newsletter["sections"], SOURCE / "newsletter.json") if newsletter.get("sections") else ""
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
    print("CMS: Verein, Mitgliedschaft, Dokumente, Newsletter und Header erzeugt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == ROOT or not (args.output / "assets/data").is_dir():
        raise SystemExit("Separates, vorbereitetes Website-Artefakt erforderlich.")
    build(args.output.resolve())
