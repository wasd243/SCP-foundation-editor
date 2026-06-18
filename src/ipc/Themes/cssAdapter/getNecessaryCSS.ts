import type { Plugin } from "postcss";

const getNecessaryCSS = (): Plugin => ({
    postcssPlugin: "getNecessaryCSS",
    Rule(rule) {
        const allUnset = rule.every(
            (node) =>
                node.type === "decl" &&
                node.value.replace(/\s*!important\s*$/, "").trim() === "unset",
        );
        if (allUnset && rule.nodes && rule.nodes.length > 0) {
            rule.remove();
        }
    },
    AtRuleExit(atRule) {
        if (!atRule.nodes || atRule.nodes.length === 0) {
            atRule.remove();
        }
    },
});

export default getNecessaryCSS;
