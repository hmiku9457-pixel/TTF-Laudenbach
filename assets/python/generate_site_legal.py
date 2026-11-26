"""Generate legal pages from CMS fields; unknown registration details stay unset."""
from __future__ import annotations
import re
from generate_site import text, seq, rich, load, render_page


def imprint_html(data):
    def lines(values):
        return "<br/>".join(text(x) for x in seq(values))

    email = data["email"]
    if not isinstance(email,str) or not re.fullmatch(r"[^@\s<>\"&]+@[^@\s<>\"&]+\.[^@\s<>\"&]+", email):
        raise ValueError("Impressum: ungültige E-Mail-Adresse")
    out = "<h2>Anbieterkennzeichnung</h2><p>" + text(data["name"]) + "<br/>" + lines(data["address"]) + "</p>"
    out += "<h2>Vertretung</h2><p>" + lines(data["board"]) + "</p>"
    court, number = data.get("register_court"), data.get("register_number")
    if bool(court) != bool(number):
        raise ValueError("Impressum: Registergericht und Registernummer gemeinsam angeben")
    if court:
        out += "<h2>Vereinsregister</h2><p>" + text(court) + "<br/>" + text(number) + "</p>"
    else:
        print("CMS-Hinweis: Vereinsregisterdaten nicht verifiziert; im Impressum ergänzen.")
    out += f'<h2>Kontakt</h2><p>E-Mail: <a href="mailto:{text(email)}">{text(email)}</a></p>'
    out += "<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2><p>" + lines(data["responsible"]) + "<br/>" + lines(data["responsible_address"]) + "</p>"
    if data.get("additional"):
        out += rich(data["additional"], "legal")
    return out


def build(output):
    legal = load("legal")
    render_page(output, "pages/footer/impressum.html", {"imprint_body": imprint_html(legal["imprint"])})
    render_page(output, "pages/footer/datenschutz.html", {"privacy_body": rich(legal["privacy"], "legal")})
