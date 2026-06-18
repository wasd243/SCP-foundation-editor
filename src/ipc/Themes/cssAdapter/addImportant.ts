import type { Plugin } from "postcss";

const addImportant = (): Plugin => ({
    postcssPlugin: "addImportant",
});

export default addImportant;
