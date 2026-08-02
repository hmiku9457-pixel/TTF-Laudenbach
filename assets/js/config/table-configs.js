import {
    formatErgebnis,
    formatUhrzeit,
    getErgebnis,
    getMannschaft,
    getSpielort
} from "../utils/game-formatters.js";

function createGameConfig(targetId, url) {
    return {
        targetId,
        url,
        cells: row => {
            const istHeimspiel = row.heim.includes("Laudenbach");
            const gegner = istHeimspiel ? row.gast : row.heim;

            return [
                row.datum,
                formatUhrzeit(row.uhrzeit),
                getSpielort(row.spielort, istHeimspiel),
                gegner,
                formatErgebnis(row.heim, row.gast, row.ergebnis)
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
        cells: row => [
            row.rang,
            row.mannschaft,
            row.partien,
            row.siege,
            row.unentschieden,
            row.niederlagen,
            row.spiele,
            row.spieleDifferenz,
            row.punkte
        ],
        emptyMessage: "Für diese Liga sind aktuell keine Tabellendaten vorhanden.",
        errorMessage: "Die Ligatabelle konnte nicht geladen werden."
    };
}

export const spieleConfigs = [
    {
        targetId: "spiele-startseite",
        url: "/assets/data/spieleStartseite.json",
        cells: spiel => {
            const istHeimspiel = spiel.heim.includes("Laudenbach");
            const gegner = istHeimspiel ? spiel.gast : spiel.heim;

            return [
                spiel.datum,
                formatUhrzeit(spiel.uhrzeit),
                getMannschaft(spiel.heim, spiel.gast, spiel.klasse),
                gegner,
                getSpielort(spiel.spielort, istHeimspiel),
                getErgebnis(spiel)
            ];
        },
        emptyMessage: "Aktuell stehen keine Spiele an.",
        errorMessage: "Die nächsten Spiele konnten nicht geladen werden."
    },
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
