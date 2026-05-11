import Underline from "@tiptap/extension-underline";
import StarterKit from "@tiptap/starter-kit";
import {
    Details,
    DetailsSummary,
} from "@tiptap/extension-details";

import { BasicExtensions } from "./extensions/btnBasicE.ts";
import { DetailsContentExtension } from "./extensions/DetailsContentE.ts";
import { FontSizeExtension } from "./extensions/FontSizeE.ts";
import { TableExtensions } from "./extensions/TableE.ts";
import { TextAlignExtension } from "./extensions/TextAlignE.ts";
import { TextColorExtension } from "./extensions/TextColorE.ts";

export const editorExtensions = [
    StarterKit,
    Underline,
    Details,
    DetailsSummary,
    DetailsContentExtension,
    TextAlignExtension,
    ...BasicExtensions,
    TextColorExtension,
    FontSizeExtension,
    ...TableExtensions,
];
