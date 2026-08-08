import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const pages = [
    "/index.html",
    "/pages/aktiverSpielbetrieb.html",
    "/pages/aktiverSpielbetrieb/herren1.html",
    "/pages/dokumente/historischeFotos.html",
    "/pages/footer/kontakt.html",
    "/404.html"
];

for (const path of pages) {
    test(`${path} lädt ohne JavaScript-Ausnahme`, async ({ page }) => {
        const pageErrors = [];
        page.on("pageerror", error => pageErrors.push(error.message));

        const response = await page.goto(path, { waitUntil: "networkidle" });
        expect(response, `Keine Antwort für ${path}`).not.toBeNull();
        expect(response.ok(), `HTTP-Fehler für ${path}`).toBeTruthy();
        await expect(page.locator("main#main-content")).toHaveCount(1);
        await expect(page.locator("main#main-content h1")).toHaveCount(1);
        await expect(page.locator('a.skip-link[href="#main-content"]')).toHaveCount(1);

        if (await page.locator("#header-container").count()) {
            await expect(page.locator("#header-container nav")).toBeVisible();
        }
        if (await page.locator("#footer-container").count()) {
            await expect(page.locator("#footer-container")).not.toBeEmpty();
        }

        expect(pageErrors).toEqual([]);
    });
}

test("Mobile Dropdown-Navigation ist explizit bedienbar", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/index.html", { waitUntil: "networkidle" });
    const toggle = page.locator(".submenu-toggle").first();
    await expect(toggle).toBeVisible();
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    await expect(page.locator(`#${await toggle.getAttribute("aria-controls")}`)).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
});

test("Kontaktformular besitzt einen zugänglichen Live-Status", async ({ page }) => {
    await page.goto("/pages/footer/kontakt.html", { waitUntil: "networkidle" });
    const status = page.locator("#contactFormStatus");
    await expect(status).toHaveAttribute("role", "status");
    await expect(status).toHaveAttribute("aria-live", "polite");
});

test("Galerie-Schaltflächen melden ihren Auswahlzustand", async ({ page }) => {
    await page.goto("/pages/dokumente/historischeFotos.html", { waitUntil: "networkidle" });
    const buttons = page.locator(".images-event-button");
    if (await buttons.count() > 0) {
        await expect(buttons.first()).toHaveAttribute("aria-pressed", /true|false/);
        if (await buttons.count() > 1) {
            await buttons.nth(1).click();
            await expect(buttons.nth(1)).toHaveAttribute("aria-pressed", "true");
        }
    }
});

test("Kernseiten haben keine kritischen Accessibility-Verstöße", async ({ page }) => {
    for (const path of ["/index.html", "/pages/aktiverSpielbetrieb.html", "/pages/footer/kontakt.html"]) {
        await page.goto(path, { waitUntil: "networkidle" });
        const results = await new AxeBuilder({ page }).analyze();
        const critical = results.violations.filter(item => item.impact === "critical");
        const serious = results.violations.filter(item => item.impact === "serious");
        if (serious.length) {
            console.warn(`${path}: ${serious.length} ernsthafte Axe-Hinweise:`, serious.map(item => item.id));
        }
        expect(critical, `${path}: kritische Axe-Verstöße`).toEqual([]);
    }
});
