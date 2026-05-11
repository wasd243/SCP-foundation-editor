import Underline from "@tiptap/extension-underline";
import StarterKit from "@tiptap/starter-kit";
import {
    DetailsSummary,
} from "@tiptap/extension-details";

import { BasicExtensions } from "./extensions/btnBasicE.ts";
import { DetailsExtension } from "./extensions/DetailsE.ts";
import { DetailsContentExtension } from "./extensions/DetailsContentE.ts";
import { FontSizeExtension } from "./extensions/FontSizeE.ts";
import { TableExtensions } from "./extensions/TableE.ts";
import { TextAlignExtension } from "./extensions/TextAlignE.ts";
import { TextColorExtension } from "./extensions/TextColorE.ts";

export const editorExtensions = [
    StarterKit,
    Underline,
    DetailsExtension,
    DetailsSummary,
    DetailsContentExtension,
    TextAlignExtension,
    ...BasicExtensions,
    TextColorExtension,
    FontSizeExtension,
    ...TableExtensions,
];
