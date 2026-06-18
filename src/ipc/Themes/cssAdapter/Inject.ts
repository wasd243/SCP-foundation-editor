export function inject(css: string) {
    const existing = document.getElementById("theme-css");
    if (existing) {
        existing.textContent = css;
    } else {
        const style = document.createElement("style");
        style.id = "theme-css";
        style.textContent = css;
        document.head.appendChild(style);
    }
}
