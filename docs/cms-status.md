---
title: "Vorschau und Veröffentlichungsstatus"
---

## Was bedeutet Speichern?

**Gespeichert** bedeutet: Pages CMS hat die redaktionelle Datei im ausgewählten Branch aktualisiert. Das ist noch keine Bestätigung der Veröffentlichung.

**In Prüfung:** Die automatisierte Inhaltsprüfung bzw. Website-Veröffentlichung läuft.

**Vorschau bereit:** Der Prüflauf ist erfolgreich. Das Artefakt cms-visuelle-vorschau herunterladen, entpacken und Vorschau.html öffnen. Die Ansicht enthält Desktop- und Mobilaufnahmen des gespeicherten Stands, auch Entwürfe eigener Unterseiten und geplante News.

**Veröffentlicht:** Nur nach erfolgreichem Live-Deployment auf main. Der aktuell ausgelieferte Commit steht im Live-Status.

**Fehler:** Den fehlgeschlagenen Workflow öffnen. Die rote Fehlermeldung nennt den technischen Grund; bei Inhaltsfehlern die betreffende Angabe im CMS korrigieren. Die letzte erfolgreich veröffentlichte Version bleibt beim Buildfehler bestehen.

- [Prüfläufe und Vorschau](https://github.com/hmiku9457-pixel/TTF-Laudenbach/actions/workflows/cms-preview.yml)
- [Veröffentlichungsläufe](https://github.com/hmiku9457-pixel/TTF-Laudenbach/actions/workflows/deploy-pages.yml)
- [Aktuell ausgelieferter Stand](https://www.ttf-laudenbach.de/redaktionsstatus.html)
- [Live-Website](https://www.ttf-laudenbach.de/)

Die CMS-Schaltfläche **Vorschau und Inhaltsprüfung** prüft den aktuellen Branch; sie veröffentlicht nichts. GitHub Actions benötigt die Workflow-Datei auf dem Standardbranch, bevor die Schaltfläche dort bzw. auf anderen Branches dispatchen kann. Die Vorschau startet außerdem automatisch nach dem Speichern.

## Entwürfe und Rechte

Eigene Unterseiten: Schalter Veröffentlichen aus = Entwurf; an = beim nächsten erfolgreichen Build auf dem jeweiligen Branch enthalten. Neuigkeiten: Zeitpunkt in der Zukunft = geplant; Zeitpunkt erreicht = zur Veröffentlichung vorgesehen. Auf dem Testbranch wird nie die Live-Website aktualisiert. Für normale redaktionelle Änderungen main wählen.

Das GitHub-Repository ist öffentlich. Entwürfe und hochgeladene Medien sind deshalb nicht vertraulich.

Redakteure können per E-Mail als Pages-CMS-Collaborator eingeladen werden. Sie bearbeiten konfigurierte Inhalte und Medien ohne GitHub-Konto. GitHub-Administratoren verwalten Konfiguration, Einladungen, Workflows und technische Dateien. Feingranulare Rechte je Inhalt oder Branch sind in Pages CMS nicht verfügbar; ein Freigabeprozess über einen Review-Branch ist eine organisatorische Regel, keine erzwungene Redaktionsrolle. Einladungen erst nach Abstimmung versenden. Keine vertraulichen Daten eintragen.
