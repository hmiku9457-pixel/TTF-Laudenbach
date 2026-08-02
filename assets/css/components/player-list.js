import { fetchJson } from "../core/http.js";
import { showTableStatus } from "../core/status.js";

export async function initSpielerliste() {
    const tbody = document.getElementById("spieler-mannschaft");

    if (!tbody) {
        return;
    }

    const datei = tbody.dataset.datei;
    const mannschaft = tbody.dataset.mannschaft;

    if (!datei || !mannschaft) {
        console.error("Spielerliste kann nicht geladen werden: data-datei oder data-mannschaft fehlt.");
        showTableStatus(tbody, "Die Spielerliste ist nicht korrekt konfiguriert.", "error");
        return;
    }

    try {
        const spielerlisten = await fetchJson(datei);
        const spieler = spielerlisten[mannschaft];

        if (!Array.isArray(spieler)) {
            throw new Error(`Mannschaft "${mannschaft}" wurde in ${datei} nicht gefunden.`);
        }

        renderSpielerliste(tbody, spieler);
    } catch (error) {
        console.error(`Fehler beim Laden der Spielerliste "${mannschaft}":`, error);
        showTableStatus(tbody, "Die Spielerliste konnte nicht geladen werden.", "error");
    }
}

function renderSpielerliste(tbody, spieler) {
    tbody.innerHTML = "";

    if (spieler.length === 0) {
        showTableStatus(tbody, "Für diese Mannschaft sind aktuell keine Spieler eingetragen.", "empty");
        return;
    }

    [...spieler]
        .sort((a, b) => Number(a.position) - Number(b.position))
        .forEach(eintrag => {
            const row = document.createElement("tr");
            [
                eintrag.position ? `${eintrag.position}.` : "–",
                eintrag.name || "Unbekannt",
                eintrag.qttr || "–"
            ].forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        });
}
