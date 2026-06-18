import type { AtRule, Plugin, Rule } from "postcss";

const KEEP_ENTRIES = [
    // IDs
    "#container-wrap", "#header", "#top-bar", "#content-wrap", "#side-bar",
    "#main-content", "#page-content", "#footer", "#breadcrumbs", "#page-title",
    // Classes
    ".meta-title", ".page-rate-widget-box", ".code",
    ".scp-image-block", ".image-block", ".footnotes-footer", ".bibitems",
    ".yui-navset", ".earthworm", ".Parallel-ACS", ".Parallel-AIM",
    ".bblock", ".dblock", ".keycap", ".tags", ".ruby", ".rt",
    ".hovertip", ".printuser", ".footer-wikiwalk-nav", ".licensebox",
    ".content-panel", ".pager", ".page-tags", ".table", ".scroll-x",
    // Elements
    "h1", "h2", "h3", "h4", "h5", "h6",
    "a", "p", "li", "ul", "ol", "blockquote", "div.blockquote", "hr",
    "table", "th", "td", "code", "pre", "tt",
    "sub", "sup", "b", "strong", "em", "small",
    // Pseudo
    ":root", "::selection", "::-webkit-scrollbar",
];

const KEEP_WILDCARD_PREFIXES = [".bg-", ".b-", ".round-", ".shadow-", ".t-", ".w-"];

const ALLOWED_AT_RULES = new Set(["media", "keyframes", "supports"]);

const BOUNDARY = /^[.:\[(]/;

function leadingToken(selector: string): string {
    const m = selector.match(/^[^\s>~+]+/);
    return m ? m[0] : selector;
}

function matchesKeepList(selector: string): boolean {
    const token = leadingToken(selector.trim());
    for (const prefix of KEEP_WILDCARD_PREFIXES) {
        if (token.startsWith(prefix)) return true;
    }
    for (const entry of KEEP_ENTRIES) {
        if (token === entry) return true;
        if (token.startsWith(entry) && BOUNDARY.test(token[entry.length]))
            return true;
    }
    return false;
}

function isInsideKeyframes(rule: Rule): boolean {
    return (
        rule.parent?.type === "atrule" &&
        (rule.parent as AtRule).name.toLowerCase().includes("keyframes")
    );
}

const getNecessaryCSS = (): Plugin => ({
    postcssPlugin: "getNecessaryCSS",
    Rule(rule) {
        if (isInsideKeyframes(rule)) return;

        const allUnset = rule.every(
            (node) =>
                node.type === "decl" &&
                node.value.replace(/\s*!important\s*$/, "").trim() === "unset",
        );
        if (allUnset && rule.nodes && rule.nodes.length > 0) {
            rule.remove();
            return;
        }

        const selectors = rule.selector.split(",").map((s) => s.trim());
        const kept = selectors.filter(matchesKeepList);
        if (kept.length === 0) {
            rule.remove();
        } else if (kept.length < selectors.length) {
            rule.selector = kept.join(", ");
        }
    },
    AtRule(atRule) {
        if (!ALLOWED_AT_RULES.has(atRule.name.toLowerCase())) {
            atRule.remove();
        }
    },
    AtRuleExit(atRule) {
        if (!atRule.nodes || atRule.nodes.length === 0) {
            atRule.remove();
        }
    },
});

export default getNecessaryCSS;
