import Underline from "@tiptap/extension-underline";
import StarterKit from "@tiptap/starter-kit";

import { BasicExtensions } from "./extensions/btnBasicE.ts";
import { DetailsExtension, DetailsSummaryExtension } from "./extensions/DetailsE.ts";
import { DetailsContentExtension } from "./extensions/DetailsContentE.ts";
import { FontSizeExtension } from "./extensions/FontSizeE.ts";
import { TableExtensions } from "./extensions/TableE.ts";
import { TabViewExtensions } from "./extensions/TabViewE.ts";
import { TextAlignExtension } from "./extensions/TextAlignE.ts";
import { TextColorExtension } from "./extensions/TextColorE.ts";

export const editorExtensions = [
    StarterKit,
    Underline,
    DetailsExtension,
    DetailsSummaryExtension,
    DetailsContentExtension,
    TextAlignExtension,
    ...BasicExtensions,
    TextColorExtension,
    FontSizeExtension,
    ...TableExtensions,
    ...TabViewExtensions,
];
