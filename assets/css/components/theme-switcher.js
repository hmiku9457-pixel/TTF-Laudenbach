export function initThemeSwitcher() {
    const switcher = document.getElementById("themeSwitcher");

    if (!switcher || switcher.dataset.themeInitialized === "true") {
        return;
    }

    switcher.dataset.themeInitialized = "true";
    switcher.addEventListener("change", event => {
        document.body.classList.remove("theme-red", "theme-dark");
        document.body.classList.add(`theme-${event.target.value}`);
    });
}
