import type { Plugin } from "postcss";

const renameCSS = (): Plugin => ({
    postcssPlugin: "renameCSS",
});

export default renameCSS;
