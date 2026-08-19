import { fetchJson } from "../core/http.js";
import { showTableStatus } from "../core/status.js";
import {
    formatErgebnis,
    formatUhrzeit,
    getMannschaft,
    getSpielort
} from "../utils/game-formatters.js";
import { refreshResponsiveTable } from "./table-responsive.js";

const PRIMARY_GAMES_URL = "/assets/data/spieleStartseite.json";
const FALLBACK_LIMIT = 8;

const TEAM_GAME_SOURCES = [
    { team: "Herren I", url: "/assets/data/spieleHerren1.json" },
    { team: "Herren II", url: "/assets/data/spieleHerren2.json" },
    { team: "Herren III", url: "/assets/data/spieleHerren3.json" },
    { team: "Herren IV", url: "/assets/data/spieleHerren4.json" },
    { team: "Herren V", url: "/assets/data/spieleHerren5.json" },
    { team: "Jugend I", url: "/assets/data/spieleJugend1.json" },
    { team: "Jugend II", url: "/assets/data/spieleJugend2.json" }
];

const text = value => value == null ? "" : String(value).trim();

function parseGameDate(game) {
    const dateMatch = text(game?.datum).match(/(\d{1,2})\.(\d{1,2})\.(\d{4})/);
    if (!dateMatch) {
        return null;
    }

    const timeMatch = text(game?.uhrzeit).match(/(\d{1,2}):(\d{2})/);
    const day = Number(dateMatch[1]);
    const month = Number(dateMatch[2]) - 1;
    const year = Number(dateMatch[3]);
    const hour = timeMatch ? Number(timeMatch[1]) : 23;
    const minute = timeMatch ? Number(timeMatch[2]) : 59;

    const date = new Date(year, month, day, hour, minute, 0, 0);
    return Number.isNaN(date.getTime()) ? null : date;
}

function gameTimestamp(game) {
    return parseGameDate(game)?.getTime() ?? Number.POSITIVE_INFINITY;
}

function hasResult(game) {
    return text(game?.ergebnis) !== "";
}

function isUpcomingGame(game, today) {
    if (hasResult(game) || text(game?.status).toLowerCase() === "gespielt") {
        return false;
    }

    const date = parseGameDate(game);
    if (!date) {
        return false;
    }

    const gameDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    return gameDay.getTime() >= today.getTime();
}

function isPastGameWithResult(game, endOfToday) {
    if (!hasResult(game)) {
        return false;
    }

    const date = parseGameDate(game);
    return Boolean(date && date.getTime() <= endOfToday.getTime());
}

function deduplicateGames(games) {
    const seen = new Set();

    return games.filter(game => {
        const key = [
            text(game?.datum),
            text(game?.uhrzeit),
            text(game?.heim),
            text(game?.gast)
        ].join("|").toLowerCase();

        if (seen.has(key)) {
            return false;
        }

        seen.add(key);
        return true;
    });
}

function getGameDisplayData(game) {
    const heim = text(game?.heim);
    const gast = text(game?.gast);
    const isHomeGame = heim.includes("Laudenbach");
    const opponent = isHomeGame ? gast : heim;
    const team = text(game?.__team)
        || getMannschaft(heim, gast, text(game?.klasse));

    return {
        heim,
        gast,
        isHomeGame,
        opponent,
        team
    };
}

function createGameCells(game, includeResult) {
    const {
        heim,
        gast,
        isHomeGame,
        opponent,
        team
    } = getGameDisplayData(game);

    const cells = [
        text(game?.datum),
        formatUhrzeit(text(game?.uhrzeit)),
        team,
        opponent,
        getSpielort(text(game?.spielort), isHomeGame)
    ];

    if (includeResult) {
        cells.push(formatErgebnis(heim, gast, text(game?.ergebnis)));
    }

    return cells;
}

function renderGames(tbody, games, {
    includeResult = false,
    emptyMessage,
    errorMessage = null
} = {}) {
    const table = tbody.closest("table");
    tbody.innerHTML = "";

    if (errorMessage) {
        showTableStatus(tbody, errorMessage, "error");
        refreshResponsiveTable(table, "next-games");
        return;
    }

    if (games.length === 0) {
        showTableStatus(tbody, emptyMessage, "empty");
        refreshResponsiveTable(table, "next-games");
        return;
    }

    games.forEach(game => {
        const row = document.createElement("tr");

        createGameCells(game, includeResult).forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value || "–";
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });

    refreshResponsiveTable(table, "next-games");
}

async function loadPrimaryGames() {
    try {
        const data = await fetchJson(PRIMARY_GAMES_URL);
        if (!Array.isArray(data)) {
            throw new Error(`${PRIMARY_GAMES_URL} enthält keine Liste.`);
        }
        return { data, failed: false };
    } catch (error) {
        console.error(`Fehler bei ${PRIMARY_GAMES_URL}:`, error);
        return { data: [], failed: true };
    }
}

async function loadTeamGames() {
    const results = await Promise.allSettled(
        TEAM_GAME_SOURCES.map(async source => {
            const data = await fetchJson(source.url);
            if (!Array.isArray(data)) {
                throw new Error(`${source.url} enthält keine Liste.`);
            }

            return data.map(game => ({
                ...game,
                __team: source.team
            }));
        })
    );

    const games = [];
    let successfulSources = 0;

    results.forEach((result, index) => {
        if (result.status === "fulfilled") {
            successfulSources += 1;
            games.push(...result.value);
            return;
        }

        console.error(
            `Fehler bei ${TEAM_GAME_SOURCES[index].url}:`,
            result.reason
        );
    });

    return {
        games,
        successfulSources,
        totalSources: TEAM_GAME_SOURCES.length
    };
}

function initViewSwitch(root) {
    if (root.dataset.homeGamesSwitchInitialized === "true") {
        return;
    }

    root.dataset.homeGamesSwitchInitialized = "true";

    const upcomingPanel = document.getElementById("home-games-upcoming");
    const pastPanel = document.getElementById("home-games-past");
    const buttons = Array.from(
        root.querySelectorAll("[data-home-games-view]")
    );

    if (!upcomingPanel || !pastPanel || buttons.length === 0) {
        return;
    }

    const setView = view => {
        const showPast = view === "past";

        upcomingPanel.hidden = showPast;
        pastPanel.hidden = !showPast;

        buttons.forEach(button => {
            const active = button.dataset.homeGamesView === view;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", String(active));
        });

        const visibleTable = (showPast ? pastPanel : upcomingPanel)
            .querySelector("table");
        refreshResponsiveTable(visibleTable, "next-games");
    };

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            setView(button.dataset.homeGamesView);
        });
    });

    setView("upcoming");
}

export async function initHomeGames() {
    const root = document.querySelector(".home-games");
    const upcomingBody = document.getElementById("spiele-startseite");
    const pastBody = document.getElementById("spiele-vergangen");

    if (!root || !upcomingBody || !pastBody) {
        return;
    }

    initViewSwitch(root);

    const now = new Date();
    const today = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate()
    );
    const endOfToday = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        23,
        59,
        59,
        999
    );

    const [primary, teamData] = await Promise.all([
        loadPrimaryGames(),
        loadTeamGames()
    ]);

    const primaryUpcoming = deduplicateGames(
        primary.data
            .filter(game => isUpcomingGame(game, today))
            .sort((a, b) => gameTimestamp(a) - gameTimestamp(b))
    );

    let upcomingGames = primaryUpcoming;

    if (upcomingGames.length === 0) {
        upcomingGames = deduplicateGames(
            teamData.games
                .filter(game => isUpcomingGame(game, today))
                .sort((a, b) => gameTimestamp(a) - gameTimestamp(b))
        ).slice(0, FALLBACK_LIMIT);
    }

    renderGames(upcomingBody, upcomingGames, {
        includeResult: false,
        emptyMessage: "Keine kommenden Spiele in den nächsten Wochen"
    });

    const historyPool = [
        ...teamData.games,
        ...primary.data
    ];

    const pastGames = deduplicateGames(
        historyPool
            .filter(game => isPastGameWithResult(game, endOfToday))
            .sort((a, b) => gameTimestamp(b) - gameTimestamp(a))
    ).slice(0, FALLBACK_LIMIT);

    const pastError = (
        pastGames.length === 0
        && (
            primary.failed
            || teamData.successfulSources < teamData.totalSources
        )
    )
        ? "Die vergangenen Spiele konnten nicht vollständig geladen werden."
        : null;

    renderGames(pastBody, pastGames, {
        includeResult: true,
        emptyMessage: "Keine vergangenen Spiele verfügbar.",
        errorMessage: pastError
    });
}
