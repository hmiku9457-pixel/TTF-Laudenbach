import { expect, test } from "@playwright/test";
import fs from "node:fs/promises";
import path from "node:path";

const routes = [
    "/",
    "/pages/unserVerein.html",
    "/pages/aktiverSpielbetrieb.html",
    "/pages/aktiverSpielbetrieb/herren1.html",
    "/pages/dokumente/historischeFotos.html",
    "/pages/footer/kontakt.html"
];

for (const route of routes) {
    test(`${route} lädt ohne strukturelle Fehler`, async ({ page }, testInfo) => {
        const consoleErrors = [];
        page.on("console", message => {
            if (message.type() === "error") consoleErrors.push(message.text());
        });
        const response = await page.goto(route, { waitUntil: "networkidle" });
        expect(response?.ok(), `HTTP-Status für ${route}`).toBeTruthy();
        await expect(page.locator("#header-container nav")).toBeVisible();
        await expect(page.locator("main#main-content")).toBeVisible();
        await expect(page.locator("#footer-container footer")).toBeVisible();
        await expect(page.locator("main#main-content h1")).toHaveCount(1);
        await expect(page.locator("header h1")).toHaveCount(0);

        const visibleH1 = page.locator("main#main-content h1");
        await expect(visibleH1).toBeVisible();

        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        expect(overflow, `Horizontaler Überlauf auf ${route}`).toBeLessThanOrEqual(2);
        expect(consoleErrors, `Konsolenfehler auf ${route}`).toEqual([]);

        const safeName = route === "/" ? "startseite" : route.replace(/^\//, "").replace(/[^a-z0-9]+/gi, "-");
        const screenshotDir = path.join("test-results", "screenshots", testInfo.project.name);
        await fs.mkdir(screenshotDir, { recursive: true });
        await page.screenshot({ path: path.join(screenshotDir, `${safeName}.png`), fullPage: true });
    });
}

test("Header und Footer sind auch ohne JavaScript vorhanden", async ({ browser }) => {
    const context = await browser.newContext({ javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.locator("#header-container nav")).toBeVisible();
    await expect(page.locator("#footer-container footer")).toBeVisible();
    await context.close();
});

test("Startseitenraster reagiert fließend", async ({ page }) => {
    await page.goto("/", { waitUntil: "networkidle" });
    const firstGrid = page.locator(".grid-home-firstLine");
    await expect(firstGrid).toBeVisible();
    const columns = await firstGrid.evaluate(element => getComputedStyle(element).gridTemplateColumns.split(" ").length);
    const viewport = page.viewportSize();
    if (viewport && viewport.width <= 1180) {
        expect(columns).toBe(1);
    } else {
        expect(columns).toBeGreaterThanOrEqual(2);
    }
});
