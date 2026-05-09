import { Mark } from "@tiptap/core";

const SubscriptExtension = Mark.create({
    name: "subscript",

    parseHTML() {
        return [{ tag: "sub" }];
    },

    renderHTML() {
        return ["sub", 0];
    },
});

const SuperscriptExtension = Mark.create({
    name: "superscript",

    parseHTML() {
        return [{ tag: "sup" }];
    },

    renderHTML() {
        return ["sup", 0];
    },
});

export const BasicExtensions = [SubscriptExtension, SuperscriptExtension];
