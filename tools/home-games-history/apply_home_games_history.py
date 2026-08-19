from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

INDEX_PATH = ROOT / "index.html"
MAIN_JS_PATH = ROOT / "assets/js/main.js"
TABLE_CONFIG_PATH = ROOT / "assets/js/config/table-configs.js"
RESPONSIVE_PATH = ROOT / "assets/js/features/table-responsive.js"
TABLES_CSS_PATH = ROOT / "assets/css/components/tables.css"
HOME_GAMES_PATH = ROOT / "assets/js/features/home-games.js"


HOME_GAMES_JS = r"""import { fetchJson } from "../core/http.js";
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
"""

OLD_INDEX_BLOCK = """<div class="next-games">
<h3 class="underline">Nächste Spiele</h3>
<table><caption class="visually-hidden">Nächste Spiele</caption>
<thead>
<tr>
<th scope="col">Datum</th>
<th scope="col">Uhrzeit</th>
<th scope="col">Mannschaft</th>
<th scope="col">Gegner</th>
<th scope="col">Spielort</th>
<th scope="col">Ergebnis</th>
</tr>
</thead>
<tbody id="spiele-startseite">
<!-- Wird per JS gefüllt -->
</tbody>
</table>
</div>"""

NEW_INDEX_BLOCK = """<div class="next-games home-games">
<h3 class="home-games-tabs" id="home-games-tabs">
<button aria-controls="home-games-upcoming" aria-pressed="true" class="home-games-tab is-active" data-home-games-view="upcoming" type="button">Nächste Spiele</button>
<span aria-hidden="true" class="home-games-tabs__separator">|</span>
<button aria-controls="home-games-past" aria-pressed="false" class="home-games-tab" data-home-games-view="past" type="button">Vergangene Spiele</button>
</h3>
<div id="home-games-upcoming">
<table><caption class="visually-hidden">Nächste Spiele</caption>
<thead>
<tr>
<th scope="col">Datum</th>
<th scope="col">Uhrzeit</th>
<th scope="col">Mannschaft</th>
<th scope="col">Gegner</th>
<th scope="col">Spielort</th>
</tr>
</thead>
<tbody id="spiele-startseite">
<!-- Wird per JS gefüllt -->
</tbody>
</table>
</div>
<div hidden id="home-games-past">
<table><caption class="visually-hidden">Vergangene Spiele</caption>
<thead>
<tr>
<th scope="col">Datum</th>
<th scope="col">Uhrzeit</th>
<th scope="col">Mannschaft</th>
<th scope="col">Gegner</th>
<th scope="col">Spielort</th>
<th scope="col">Ergebnis</th>
</tr>
</thead>
<tbody id="spiele-vergangen">
<!-- Wird per JS gefüllt -->
</tbody>
</table>
</div>
</div>"""

OLD_FORMATTER_IMPORT = """import {
    formatErgebnis,
    formatUhrzeit,
    getErgebnis,
    getMannschaft,
    getSpielort
} from "../utils/game-formatters.js";"""

NEW_FORMATTER_IMPORT = """import {
    formatErgebnis,
    formatUhrzeit,
    getSpielort
} from "../utils/game-formatters.js";"""

OLD_STARTPAGE_CONFIG = """export const spieleConfigs = [
    {
        targetId: "spiele-startseite",
        url: "/assets/data/spieleStartseite.json",
        responsiveType: "next-games",
        cells: spiel => {
            const heim = text(spiel?.heim);
            const gast = text(spiel?.gast);
            const istHeimspiel = heim.includes("Laudenbach");
            const gegner = istHeimspiel ? gast : heim;
            return [
                text(spiel?.datum),
                formatUhrzeit(text(spiel?.uhrzeit)),
                getMannschaft(heim, gast, text(spiel?.klasse)),
                gegner,
                getSpielort(text(spiel?.spielort), istHeimspiel),
                getErgebnis({ ...spiel, heim, gast })
            ];
        },
        emptyMessage: "Aktuell stehen keine Spiele an.",
        errorMessage: "Die nächsten Spiele konnten nicht geladen werden."
    },
    createGameConfig"""

NEW_STARTPAGE_CONFIG = """export const spieleConfigs = [
    createGameConfig"""

OLD_MAIN_NEWS_BLOCK = """    if (has(".news-slider")) {
        tasks.push(loadFeature("./features/news-slider.js", "initNewsSlider"));
    }
"""

NEW_MAIN_NEWS_BLOCK = OLD_MAIN_NEWS_BLOCK + """    if (has("#home-games-tabs")) {
        tasks.push(loadFeature("./features/home-games.js", "initHomeGames"));
    }
"""

OLD_RESPONSIVE_GUARD = """            if (cells.length < NEXT_GAMES_COLUMN_NAMES.length) {
                return;
            }"""

NEW_RESPONSIVE_GUARD = """            if (cells.length < 5) {
                return;
            }"""

CSS_MARKER = "/* ===== STARTSEITE: NÄCHSTE / VERGANGENE SPIELE ===== */"

CSS_APPEND = r"""
/* ===== STARTSEITE: NÄCHSTE / VERGANGENE SPIELE ===== */
.home-games-tabs {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
}

.home-games-tab {
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--text-muted);
    font: inherit;
    cursor: pointer;
}

.home-games-tab:hover,
.home-games-tab.is-active {
    color: var(--accent);
}

.home-games-tab.is-active {
    text-decoration: underline;
    text-decoration-thickness: 2px;
    text-underline-offset: 0.3em;
}

.home-games-tab:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 4px;
    border-radius: var(--space-s);
}

.home-games-tabs__separator {
    color: var(--text-muted);
}
"""


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(path, old, new, already_present, label):
    content = read(path)

    if already_present in content:
        print(f"[OK] {label}: bereits angewendet.")
        return False

    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"{label}: erwarteter Ausgangsblock wurde {count}x gefunden. "
            "Abbruch, damit keine unbekannte Repo-Version beschädigt wird."
        )

    write(path, content.replace(old, new, 1))
    print(f"[GEÄNDERT] {label}")
    return True


def write_home_games_feature():
    existing = read(HOME_GAMES_PATH) if HOME_GAMES_PATH.exists() else None
    if existing == HOME_GAMES_JS:
        print("[OK] home-games.js: bereits aktuell.")
        return False

    write(HOME_GAMES_PATH, HOME_GAMES_JS)
    print("[GEÄNDERT] assets/js/features/home-games.js")
    return True


def update_css():
    content = read(TABLES_CSS_PATH)
    if CSS_MARKER in content:
        print("[OK] Tabellen-CSS: Startseiten-Umschalter bereits vorhanden.")
        return False

    write(TABLES_CSS_PATH, content.rstrip() + "\n\n" + CSS_APPEND.strip() + "\n")
    print("[GEÄNDERT] assets/css/components/tables.css")
    return True


def main():
    changed = False

    changed |= replace_once(
        INDEX_PATH,
        OLD_INDEX_BLOCK,
        NEW_INDEX_BLOCK,
        'id="home-games-tabs"',
        "index.html / Startseiten-Spielkarte"
    )

    changed |= replace_once(
        MAIN_JS_PATH,
        OLD_MAIN_NEWS_BLOCK,
        NEW_MAIN_NEWS_BLOCK,
        'loadFeature("./features/home-games.js", "initHomeGames")',
        "main.js / Home-Games-Initialisierung"
    )

    changed |= replace_once(
        TABLE_CONFIG_PATH,
        OLD_FORMATTER_IMPORT,
        NEW_FORMATTER_IMPORT,
        "formatUhrzeit,\n    getSpielort",
        "table-configs.js / ungenutzte Imports"
    )

    changed |= replace_once(
        TABLE_CONFIG_PATH,
        OLD_STARTPAGE_CONFIG,
        NEW_STARTPAGE_CONFIG,
        'export const spieleConfigs = [\n    createGameConfig',
        "table-configs.js / Startseiten-Sonderkonfiguration"
    )

    changed |= replace_once(
        RESPONSIVE_PATH,
        OLD_RESPONSIVE_GUARD,
        NEW_RESPONSIVE_GUARD,
        "if (cells.length < 5)",
        "table-responsive.js / 5- oder 6-spaltige Startseitentabelle"
    )

    changed |= write_home_games_feature()
    changed |= update_css()

    if changed:
        print("\nUpdate erfolgreich angewendet.")
    else:
        print("\nKeine Änderungen nötig. Das Paket ist bereits vollständig angewendet.")


if __name__ == "__main__":
    main()
