export function getMannschaft(heim, gast, klasse) {
    let team = "";

    if (heim.includes("Laudenbach")) {
        team = heim;
    } else if (gast.includes("Laudenbach")) {
        team = gast;
    } else {
        return "-";
    }

    const match = team.match(/(I|II|III|IV|V)$/);
    const nummer = match ? match[0] : "I";

    if (klasse.startsWith("J")) {
        return `Jugend ${nummer}`;
    }

    if (klasse.startsWith("E")) {
        return `Herren ${nummer}`;
    }

    return nummer;
}

export function getSpielort(code, istHeimspiel) {
    if (!istHeimspiel) {
        return "Auswärtsspiel";
    }

    switch (code) {
        case "1":
            return "Großsporthalle Weikersheim";
        case "2":
            return "Zehntscheune Laudenbach";
        case "3":
            return "Ausweichhalle";
        default:
            return "Unbekannt";
    }
}

export function formatUhrzeit(uhrzeit) {
    if (!uhrzeit) {
        return "–";
    }

    return String(uhrzeit)
        .replace("\n", " ")
        .replace(/\s+v$/, " v");
}

export function getErgebnis(spiel) {
    return spiel.status === "geplant" ? "-:-" : spiel.ergebnis || "-:-";
}

export function formatErgebnis(heim, _gast, ergebnis) {
    if (!ergebnis) {
        return "-:-";
    }

    const [heimPunkte, gastPunkte] = ergebnis.split(":").map(Number);

    if (!Number.isFinite(heimPunkte) || !Number.isFinite(gastPunkte)) {
        return ergebnis;
    }

    return heim.includes("TTF Laudenbach")
        ? `${heimPunkte}:${gastPunkte}`
        : `${gastPunkte}:${heimPunkte}`;
}

// Ergebnisse werden immer aus Sicht der TTF Laudenbach gewertet.
export function getGameOutcome(heim, gast, ergebnis) {
    const homeIsTtf = String(heim ?? "").includes("TTF Laudenbach");
    const awayIsTtf = String(gast ?? "").includes("TTF Laudenbach");
    const score = String(ergebnis ?? "").trim().match(/^(\d+)\s*:\s*(\d+)$/);

    if (homeIsTtf === awayIsTtf || !score) {
        return null;
    }

    const homePoints = Number(score[1]);
    const awayPoints = Number(score[2]);
    const ownPoints = homeIsTtf ? homePoints : awayPoints;
    const opponentPoints = homeIsTtf ? awayPoints : homePoints;

    if (ownPoints === opponentPoints) {
        return "draw";
    }

    return ownPoints > opponentPoints ? "win" : "loss";
}

export function highlightGameResult(cell, heim, gast, ergebnis) {
    if (!cell) {
        return;
    }

    const outcome = getGameOutcome(heim, gast, ergebnis);
    if (!outcome) {
        return;
    }

    const labels = {
        win: "Sieg",
        loss: "Niederlage",
        draw: "Unentschieden"
    };
    const label = labels[outcome];

    cell.classList.add(`game-result--${outcome}`);
    cell.title = label;
    cell.setAttribute("aria-label", `${label}: ${cell.textContent}`);
}
