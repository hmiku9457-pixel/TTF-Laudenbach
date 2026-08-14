# GitHub-Pages-Deployment

Die Website wird zentral über den Workflow **Website veröffentlichen** auf GitHub Pages deployed.

## Einmalige Umstellung

Nach dem Einspielen dieses Pakets in GitHub:

1. Repository öffnen.
2. **Settings** öffnen.
3. Unter **Code and automation** → **Pages** wechseln.
4. Unter **Build and deployment** bei **Source** `GitHub Actions` auswählen.
5. Danach unter **Actions** den Workflow **Website veröffentlichen** einmal manuell starten.
6. Website anschließend auf Desktop und Mobil prüfen.

Solange `Deploy from a branch` aktiv ist, startet GitHub weiterhin den eingebauten Workflow `pages-build-deployment`.
Nach der Umstellung auf `GitHub Actions` übernimmt ausschließlich der eigene Workflow.

## Zuständigkeiten

### Website veröffentlichen

Der Workflow `.github/workflows/deploy-pages.yml` besitzt drei Einstiege:

* direkter Push von öffentlich wirksamen Website-Dateien,
* manueller `workflow_dispatch`,
* Aufruf als wiederverwendbarer Workflow durch Generatoren.

Er deployed immer den aktuellen Stand von `main`.

### News generieren

`generate-news.yml` erzeugt und committed News-Ausgaben.

Danach wird **Website veröffentlichen** aufgerufen:

* wenn sich generierte News-Dateien geändert haben,
* nach einem News-Push, damit auch reine Bildänderungen veröffentlicht werden,
* bei einem manuellen Rebuild.

Bei reinen geplanten Checks ohne Änderung wird nicht deployed.

### Generate Gallery JSON

Der Galerie-Workflow verarbeitet normale Galerie-/Website-Bilder unter `assets/images/`.

Ausgenommen sind:

* `assets/images/seo/` – direkte Website-Dateien, kein Galerie-Input,
* `assets/images/news/` – eigene Medienquelle des News-CMS.

Nach einem erfolgreichen Galerie-Lauf wird zentral deployed, damit auch reine Bildänderungen ohne JSON-Diff veröffentlicht werden.

### Auto-Update Daten

Der Scraper deployed nur dann, wenn tatsächlich neue oder geänderte JSON-Daten committed wurden.

## Öffentliches Pages-Artefakt

Der Deployment-Workflow kopiert bewusst nur Dateien, die der Browser benötigt:

* `index.html`
* `404.html`
* `CNAME`
* `robots.txt`
* `sitemap.xml`
* `components/`
* `pages/`
* `assets/css/`
* `assets/data/`
* `assets/images/`
* `assets/js/`

Nicht veröffentlicht werden unter anderem:

* `assets/python/`
* `content/news/`
* `templates/`
* `.pages.yml`
* `docs/`
* Repository- und Workflow-Dateien

Damit bleibt die Website statisch, während technische Quellen nicht Bestandteil des Pages-Artefakts sind.

## Manueller Repair

Wenn die Website einmal nicht dem aktuellen `main`-Stand entspricht:

**Actions → Website veröffentlichen → Run workflow**

Für inkonsistente News zuerst:

**Actions → News generieren → Run workflow**

Dieser Workflow ruft die Veröffentlichung nach dem Rebuild selbst auf.
