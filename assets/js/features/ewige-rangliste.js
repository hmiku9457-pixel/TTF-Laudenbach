import { fetchJson } from "../core/http.js";

const DATA_URL = "/assets/data/ewigeRangliste.json";
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function germanDate(iso) {
    if (!DATE_RE.test(iso || "")) return "unbekannt";
    const [year, month, day] = iso.split("-");
    return [day, month, year].join(".");
}

function csvCell(value) {
    // Keine Excel-Formeln aus Vereinsdaten ausführen.
    let text = String(value ?? "");
    if (/^[=+@-]/.test(text)) text = "'" + text;
    return '"' + text.replace(/"/g, '""') + '"';
}

function downloadMaster(data) {
    if (!DATE_RE.test(data.exportStichtag)) {
        throw new Error("Export-Stichtag fehlt.");
    }
    const players = [...data.spieler]
        .map(item => ({ name: item.name, spiele: item.exportSpiele }))
        .filter(item => Number.isInteger(item.spiele) && item.spiele > 0)
        .sort((a, b) => b.spiele - a.spiele || a.name.localeCompare(b.name, "de"));

    const rows = [
        ["Stand", germanDate(data.exportStichtag)],
        ["Name", "Spiele"],
        ...players.map(item => [item.name, String(item.spiele)])
    ];
    const body = "\uFEFF" + rows.map(row => row.map(csvCell).join(";")).join("\r\n") + "\r\n";
    const blob = new Blob([body], { type: "text/csv;charset=utf-8" });
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = "ewige-rangliste-master-" + data.exportStichtag + ".csv";
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
}

export async function initEwigeRangliste() {
    const tbody = document.getElementById("rangliste-body");
    const status = document.getElementById("rangliste-status");
    const stand = document.getElementById("rangliste-stand");
    const button = document.getElementById("rangliste-export");
    const search = document.getElementById("searchInput");
    if (!tbody || !status || !button || !stand) return;

    try {
        const data = await fetchJson(DATA_URL, { cache: "no-cache" });
        if (!Array.isArray(data.spieler) || !DATE_RE.test(data.masterStichtag)) {
            throw new Error("Ranglistendaten haben ein ungültiges Format.");
        }
        tbody.replaceChildren();
        const fragment = document.createDocumentFragment();
        for (const item of data.spieler) {
            const row = document.createElement("tr");
            const rank = document.createElement("th");
            rank.scope = "row";
            rank.textContent = String(item.rang);
            const name = document.createElement("td");
            name.textContent = item.name;
            const games = document.createElement("td");
            games.textContent = Number(item.spiele).toLocaleString("de-DE");
            row.append(rank, name, games);
            fragment.append(row);
        }
        tbody.append(fragment);
        const dateLabel = germanDate(data.exportStichtag);
        stand.textContent = "Master: " + germanDate(data.masterStichtag) +
            " · Sicherer CSV-Export bis: " + dateLabel +
            (data.zuletztGeprueft ? " · Letzte Prüfung: " +
                new Date(data.zuletztGeprueft).toLocaleString("de-DE") : "");
        const isUncertain = Boolean(data.unvollstaendig);
        status.classList.toggle("ranking-status--warning", isUncertain);
        status.textContent = isUncertain
            ? "Hinweis: Die Daten sind möglicherweise unvollständig (" +
                (data.anzahlFehler || 0) + " offene Prüfhinweise). Der Export ist auf den " +
                dateLabel + " begrenzt."
            : "Alle bisher erfassten Erwachsenenbegegnungen wurden ausgewertet.";
        button.disabled = false;
        button.addEventListener("click", () => downloadMaster(data));
        // Die generierten Tabellenzeilen auch bei bereits eingegebenem Suchtext filtern.
        search?.dispatchEvent(new Event("input"));
    } catch (error) {
        console.error("Ewige Rangliste:", error);
        tbody.replaceChildren();
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 3;
        cell.textContent = "Die Ewige Rangliste konnte nicht geladen werden.";
        row.append(cell);
        tbody.append(row);
        status.textContent = "Datenabruf fehlgeschlagen. Bitte später erneut versuchen.";
        status.classList.add("ranking-status--warning");
        button.disabled = true;
    }
}
