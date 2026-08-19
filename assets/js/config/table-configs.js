import {
    formatErgebnis,
    formatUhrzeit,
    getSpielort
} from "../utils/game-formatters.js";

const text = value => value == null ? "" : String(value);

function createGameConfig(targetId, url) {
    return {
        targetId,
        url,
        responsiveType: "schedule",
        cells: row => {
            const heim = text(row?.heim);
            const gast = text(row?.gast);
            const istHeimspiel = heim.includes("Laudenbach");
            const gegner = istHeimspiel ? gast : heim;
            return [
                text(row?.datum),
                formatUhrzeit(text(row?.uhrzeit)),
                getSpielort(text(row?.spielort), istHeimspiel),
                gegner,
                formatErgebnis(heim, gast, text(row?.ergebnis))
            ];
        },
        emptyMessage: "Für diese Mannschaft sind aktuell keine Spiele eingetragen.",
        errorMessage: "Der Spielplan konnte nicht geladen werden."
    };
}

function createLeagueTableConfig(targetId, url) {
    return {
        targetId,
        url,
        responsiveType: "league",
        cells: row => [
            text(row?.rang),
            text(row?.mannschaft),
            text(row?.partien),
            text(row?.siege),
            text(row?.unentschieden),
            text(row?.niederlagen),
            text(row?.spiele),
            text(row?.spieleDifferenz),
            text(row?.punkte)
        ],
        emptyMessage: "Für diese Liga sind aktuell keine Tabellendaten vorhanden.",
        errorMessage: "Die Ligatabelle konnte nicht geladen werden."
    };
}

export const spieleConfigs = [
    createGameConfig("spiele-herren1", "/assets/data/spieleHerren1.json"),
    createGameConfig("spiele-herren2", "/assets/data/spieleHerren2.json"),
    createGameConfig("spiele-herren3", "/assets/data/spieleHerren3.json"),
    createGameConfig("spiele-herren4", "/assets/data/spieleHerren4.json"),
    createGameConfig("spiele-herren5", "/assets/data/spieleHerren5.json"),
    createGameConfig("spiele-jugend1", "/assets/data/spieleJugend1.json"),
    createGameConfig("spiele-jugend2", "/assets/data/spieleJugend2.json")
];

export const tabellenConfigs = [
    createLeagueTableConfig("tabelle-herren1", "/assets/data/tabelleHerren1.json"),
    createLeagueTableConfig("tabelle-herren2", "/assets/data/tabelleHerren2.json"),
    createLeagueTableConfig("tabelle-herren3", "/assets/data/tabelleHerren3.json"),
    createLeagueTableConfig("tabelle-herren4", "/assets/data/tabelleHerren4.json"),
    createLeagueTableConfig("tabelle-herren5", "/assets/data/tabelleHerren5.json"),
    createLeagueTableConfig("tabelle-jugend1", "/assets/data/tabelleJugend1.json"),
    createLeagueTableConfig("tabelle-jugend2", "/assets/data/tabelleJugend2.json")
];
