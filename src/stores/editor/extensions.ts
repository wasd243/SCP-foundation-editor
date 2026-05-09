import Underline from "@tiptap/extension-underline";
import StarterKit from "@tiptap/starter-kit";
import { BasicExtensions } from "./extensions/btnBasicE.ts";
import { FontSizeExtension } from "./extensions/FontSizeE.ts";
import { TableExtensions } from "./extensions/TableE.ts";
import { TextAlignExtension } from "./extensions/TextAlignE.ts";
import { TextColorExtension } from "./extensions/TextColorE.ts";

export const editorExtensions = [
    StarterKit,
    Underline,
    TextAlignExtension,
    ...BasicExtensions,
    TextColorExtension,
    FontSizeExtension,
    ...TableExtensions,
];
