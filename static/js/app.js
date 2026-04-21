const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");
const themeToggle = document.querySelector(".theme-toggle");
const themeToggleText = document.querySelector(".theme-toggle__text");

function getStoredTheme() {
    return window.localStorage.getItem("ips-theme");
}

function getPreferredTheme() {
    const storedTheme = getStoredTheme();
    if (storedTheme === "dark" || storedTheme === "light") {
        return storedTheme;
    }

    return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
}

function applyTheme(theme, persist = true) {
    document.documentElement.setAttribute("data-theme", theme);

    if (persist) {
        window.localStorage.setItem("ips-theme", theme);
    }

    if (themeToggle && themeToggleText) {
        const nextTheme = theme === "dark" ? "light" : "dark";
        themeToggle.setAttribute("aria-pressed", String(theme === "dark"));
        themeToggle.setAttribute("aria-label", `Switch to ${nextTheme} theme`);
        themeToggleText.textContent = nextTheme === "dark" ? "Dark Theme" : "Light Theme";
    }
}

if (themeToggle) {
    applyTheme(getPreferredTheme(), false);

    themeToggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
        applyTheme(currentTheme === "dark" ? "light" : "dark");
    });
}

if (menuToggle && siteNav) {
    menuToggle.addEventListener("click", () => {
        const isOpen = siteNav.classList.toggle("is-open");
        menuToggle.setAttribute("aria-expanded", String(isOpen));
    });
}

document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        const message = form.dataset.confirm || "Are you sure?";
        if (!window.confirm(message)) {
            event.preventDefault();
        }
    });
});

const sectionInput = document.getElementById("section");
if (sectionInput) {
    sectionInput.addEventListener("input", () => {
        sectionInput.value = sectionInput.value.toUpperCase();
    });
}
