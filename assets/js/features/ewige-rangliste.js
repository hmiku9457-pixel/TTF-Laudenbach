import { fetchJson } from "../core/http.js";

const DATA_URL = "/assets/data/ewigeRangliste.json";
const SEASON_URL = "/assets/data/ewigeRanglisteSaison.json";
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


function playerKey(name) {
    return String(name ?? "").normalize("NFKC")
        .replace(/\s+/g, " ").trim().toLocaleLowerCase("de-DE");
}

function appendCell(row, tagName, value, className) {
    const cell = document.createElement(tagName);
    if (tagName === "th") cell.scope = "row";
    if (className) cell.className = className;
    cell.textContent = value;
    row.appendChild(cell);
    return cell;
}

function showSeasonDetails(item, seasonData, previousTotal, index, available) {
    const registered = Boolean(seasonData?.gemeldet);
    const currentSeason = available && Number.isInteger(seasonData?.einsätze)
        ? seasonData.einsätze : (available ? 0 : null);
    const seasonLabel = currentSeason === null ? "–"
        : (!registered && currentSeason === 0 ? "–" : String(currentSeason));
    const total = Number(item.spiele);
    const gap = index === 0 ? null : Math.max(0, previousTotal - total);
    return { registered, seasonLabel, gapLabel: gap === null ? "–" : String(gap) };
}

export async function initEwigeRangliste() {
    const tbody = document.getElementById("rangliste-body");
    const status = document.getElementById("rangliste-status");
    const stand = document.getElementById("rangliste-stand");
    const button = document.getElementById("rangliste-export");
    const search = document.getElementById("searchInput");
    const seasonInfo = document.getElementById("rangliste-saisoninfo");
    if (!tbody || !status || !button || !stand) return;

    try {
        // Die Rangliste bleibt nutzbar, selbst wenn optionale Saisoninformationen fehlen.
        const [data, seasonRequest] = await Promise.all([
            fetchJson(DATA_URL, { cache: "no-cache" }),
            fetchJson(SEASON_URL, { cache: "no-cache" }).catch(error => {
                console.warn("Saisoninformationen konnten nicht geladen werden:", error);
                return null;
            })
        ]);
        const seasonData = seasonRequest && Array.isArray(seasonRequest.spieler) ? seasonRequest : null;
        const seasonIndex = new Map((seasonData?.spieler || []).map(item => [playerKey(item.name), item]));
        const available = Boolean(seasonData);
        if (!Array.isArray(data.spieler) || !DATE_RE.test(data.masterStichtag)) {
            throw new Error("Ranglistendaten haben ein ungültiges Format.");
        }
        tbody.replaceChildren();
        const fragment = document.createDocumentFragment();
        for (const [index, item] of data.spieler.entries()) {
            const row = document.createElement("tr");
            const previous = index === 0 ? 0 : Number(data.spieler[index - 1].spiele);
            const detail = showSeasonDetails(item, seasonIndex.get(playerKey(item.name)),
                previous, index, available);
            if (detail.registered) {
                row.classList.add("ranking-player--registered");
                row.title = "Für diese Saison gemeldet";
            }
            appendCell(row, "th", String(item.rang), "ranking-cell-rank");
            const name = appendCell(row, "td", "", "ranking-cell-name");
            const nameSpan = document.createElement("span");
            nameSpan.className = "ranking-player-name";
            nameSpan.textContent = item.name;
            name.append(nameSpan);
            if (detail.registered) {
                const hiddenText = document.createElement("span");
                hiddenText.className = "visually-hidden";
                hiddenText.textContent = " – für diese Saison gemeldet";
                name.append(hiddenText);
            }
            const mobile = document.createElement("small");
            mobile.className = "ranking-mobile-details";
            mobile.textContent = "Saison: " + detail.seasonLabel +
                " · Rückstand: " + detail.gapLabel;
            name.append(mobile);
            appendCell(row, "td", Number(item.spiele).toLocaleString("de-DE"),
                "ranking-cell-number ranking-cell-total");
            appendCell(row, "td", detail.seasonLabel,
                "ranking-cell-number ranking-cell-season");
            appendCell(row, "td", detail.gapLabel,
                "ranking-cell-number ranking-cell-gap");
            fragment.append(row);
        }
        tbody.append(fragment);
        if (seasonInfo) {
            if (seasonData) {
                seasonInfo.textContent = "Saison " + seasonData.saison + " · " +
                    Number(seasonData.erfassteBegegnungen || 0) +
                    " Begegnungen erfasst · Markierte Spieler sind aktuell für Erwachsenenmannschaften gemeldet." +
                    (seasonData.unvollstaendig ? " Einzelne Saisonberichte sind möglicherweise noch unvollständig." : "");
            } else {
                seasonInfo.textContent = "Saisoninformationen derzeit nicht verfügbar. Die Gesamteinsätze bleiben sichtbar.";
            }
        }
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
        cell.colSpan = 5;
        cell.textContent = "Die Ewige Rangliste konnte nicht geladen werden.";
        row.append(cell);
        tbody.append(row);
        status.textContent = "Datenabruf fehlgeschlagen. Bitte später erneut versuchen.";
        if (seasonInfo) seasonInfo.textContent = "";
        status.classList.add("ranking-status--warning");
        button.disabled = true;
    }
}
