#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "pages/unserVerein.html"
CSS = ROOT / "assets/css/layout/grid-boxes.css"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"{label}: erwarteter aktueller Abschnitt wurde nicht gefunden.")
    return text.replace(old, new, 1)


def update_html() -> None:
    text = HTML.read_text(encoding="utf-8")

    old = '''<div class="column">
<div class="box">
<h2 class="u-text-center">Die Tischtennisfreunde Laudenbach</h2>
<p>Als eigenständiger Verein gingen die TTF 1975 aus der Tischtennisabteilung des TSV Laudenbach hervor.</p>
<p>Bald schon stellten sich erste sportliche Erfolge ein.</p>
<p>Die Mannschaften aus dem Vorbachtal konnten zahlreiche Meisterschaften im Jugend- und Erwachsenenbereich erringen.</p>
<p>Auch im gesellschaftlichen Leben des Weikersheimer Teilortes wurde man eine anerkannte Größe. Neben der Organisation des sogenannten "Sommernachtsfestes" sowie alljährlichen Weinproben und den traditionellen Nikolausfeiern engagieren sich die Ballkünstler im Rahmen des Faschingsumzuges.</p>
<p>Lange Jahre prägte die engagierte Vorstandschaft unter dem Vorsitz des umtriebigen Vorsitzenden Johannes Scherrer das Vereinsleben nach innen und außen.</p>
<p>In der jüngeren Vergangenheit setzte das Vorstandsteam um den tatkräftigen neuen Vorsitzenden Thomas Ruske diese Tradition fort.</p>
<p>Seit dem Jahr 2017 ist Manfred Litwitz gemeinsam mit der umstrukturierten Vorstandsmannschaft für die Geschicke des Vereins verantwortlich.</p>
</div>
<div class="grid-button">
<a class="button button--card" href="/pages/dokumente/04.05.2011_TTF_Satzung_v1.1.pdf" rel="noopener noreferrer" target="_blank">Hier kann die Satzung eingesehen werden</a>
</div>
</div>'''

    new = '''<div class="club-info">
<div class="box">
<h2 class="u-text-center">Die Tischtennisfreunde Laudenbach</h2>
<p>Als eigenständiger Verein gingen die TTF 1975 aus der Tischtennisabteilung des TSV Laudenbach hervor.</p>
<p>Bald schon stellten sich erste sportliche Erfolge ein.</p>
<p>Die Mannschaften aus dem Vorbachtal konnten zahlreiche Meisterschaften im Jugend- und Erwachsenenbereich erringen.</p>
<p>Auch im gesellschaftlichen Leben des Weikersheimer Teilortes wurde man eine anerkannte Größe. Neben der Organisation des sogenannten "Sommernachtsfestes" sowie alljährlichen Weinproben und den traditionellen Nikolausfeiern engagieren sich die Ballkünstler im Rahmen des Faschingsumzuges.</p>
<p>Lange Jahre prägte die engagierte Vorstandschaft unter dem Vorsitz des umtriebigen Vorsitzenden Johannes Scherrer das Vereinsleben nach innen und außen.</p>
<p>In der jüngeren Vergangenheit setzte das Vorstandsteam um den tatkräftigen neuen Vorsitzenden Thomas Ruske diese Tradition fort.</p>
<p>Seit dem Jahr 2017 ist Manfred Litwitz gemeinsam mit der umstrukturierten Vorstandsmannschaft für die Geschicke des Vereins verantwortlich.</p>
</div>
<a class="button button--card club-info__statutes" href="/pages/dokumente/04.05.2011_TTF_Satzung_v1.1.pdf" rel="noopener noreferrer" target="_blank">Hier kann die Satzung eingesehen werden</a>
</div>'''

    text = replace_once(text, old, new, "pages/unserVerein.html")
    HTML.write_text(text, encoding="utf-8")


def update_css() -> None:
    text = CSS.read_text(encoding="utf-8")

    old_full_width = '''/* Unser Verein: Satzungslink nutzt die volle Breite der linken Spalte. */
.column > .grid-button:has(> a[href$="04.05.2011_TTF_Satzung_v1.1.pdf"]) {
    padding: 0;
}
.column > .grid-button:has(> a[href$="04.05.2011_TTF_Satzung_v1.1.pdf"]) > .button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 64px;
}

'''
    text = text.replace(old_full_width, "", 1)

    old_spacing = '''/*
 * Unser Verein:
 * .grid-button besitzt global margin-top: auto und wird dadurch in der
 * gestreckten linken Spalte nach unten geschoben. Für den Satzungsbereich
 * wird dieses Verhalten bewusst aufgehoben und ein definierter Abstand gesetzt.
 */
.column:has(> .grid-button > a[href$="04.05.2011_TTF_Satzung_v1.1.pdf"]) {
    align-content: start;
    gap: var(--space-xl);
}
.column > .grid-button:has(> a[href$="04.05.2011_TTF_Satzung_v1.1.pdf"]) {
    margin-top: 0;
}

'''
    text = text.replace(old_spacing, "", 1)

    old_mobile = '''    .column > .grid-button:has(> a[href$="04.05.2011_TTF_Satzung_v1.1.pdf"]) {
        padding-right: 0;
        padding-left: 0;
    }
'''
    text = text.replace(old_mobile, "", 1)

    anchor = '''.column {
    display: grid;
    gap: var(--space-m);
}
'''

    addition = '''.column {
    display: grid;
    gap: var(--space-m);
}

/*
 * Unser Verein: analog zum Startseiten-Prinzip "Inhalt + direkter CTA".
 * Die Höhe der benachbarten Ausschuss-Box beeinflusst den Satzungsbutton nicht.
 */
.club-info {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: var(--space-m);
    align-self: start;
}

.club-info__statutes {
    display: flex;
    align-items: center;
    justify-content: center;
    align-self: stretch;
    min-height: 64px;
    padding: var(--space-m) var(--space-l);
    text-align: center;
}
'''

    if ".club-info__statutes {" not in text:
        if anchor not in text:
            raise RuntimeError("grid-boxes.css: .column-Grundregel wurde nicht gefunden.")
        text = text.replace(anchor, addition, 1)

    if 'a[href$="04.05.2011_TTF_Satzung_v1.1.pdf"]' in text:
        raise RuntimeError(
            "grid-boxes.css: alte Satzungs-Sonderregel ist nach dem Cleanup noch vorhanden."
        )

    CSS.write_text(text, encoding="utf-8")


def validate() -> None:
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    if html.count('class="club-info"') != 1:
        raise RuntimeError("Unser Verein: club-info muss genau einmal vorhanden sein.")
    if html.count("club-info__statutes") != 1:
        raise RuntimeError("Unser Verein: Satzungsbutton-Struktur ist nicht eindeutig.")
    if '<div class="grid-button">\n<a class="button button--card" href="/pages/dokumente/04.05.2011_TTF_Satzung_v1.1.pdf"' in html:
        raise RuntimeError("Unser Verein: alte grid-button-Struktur ist noch vorhanden.")

    if ".club-info {" not in css or ".club-info__statutes {" not in css:
        raise RuntimeError("grid-boxes.css: neue Vereinsregeln fehlen.")
    if css.count("{") != css.count("}"):
        raise RuntimeError("grid-boxes.css: unausgeglichene geschweifte Klammern.")


def main() -> None:
    update_html()
    update_css()
    validate()
    print("Unser-Verein-Button-Struktur erfolgreich angepasst.")


if __name__ == "__main__":
    main()
