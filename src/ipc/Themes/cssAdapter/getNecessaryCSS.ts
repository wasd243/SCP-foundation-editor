import type { Plugin } from "postcss";

const getNecessaryCSS = (): Plugin => ({
    postcssPlugin: "getNecessaryCSS",
});

export default getNecessaryCSS;
