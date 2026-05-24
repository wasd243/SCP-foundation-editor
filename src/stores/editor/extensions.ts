import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import StarterKit from "@tiptap/starter-kit";
import Image from "@tiptap/extension-image";

import { BasicExtensions } from "./extensions/btnBasicE.ts";
import { CodeBlockLowlightExtension } from "./extensions/CodeE.ts";
import { DetailsExtension, DetailsSummaryExtension } from "./extensions/DetailsE.ts";
import { DetailsContentExtension } from "./extensions/DetailsContentE.ts";
import { FontSizeExtension } from "./extensions/FontSizeE.ts";
import { TableExtensions } from "./extensions/TableE.ts";
import { TabViewExtensions } from "./extensions/TabViewE.ts";
import { TextAlignExtension } from "./extensions/TextAlignE.ts";
import { TextColorExtension } from "./extensions/TextColorE.ts";
import { WJTagExtension } from "./extensions/WJtagsE.ts";

export const editorExtensions = [
    StarterKit.configure({
        codeBlock: false,
    }),
    Underline,
    Link.configure({
        openOnClick: false,
    }),
    Image.configure({
        inline: false,
        allowBase64: false,
    }),
    CodeBlockLowlightExtension,
    DetailsExtension,
    DetailsSummaryExtension,
    DetailsContentExtension,
    TextAlignExtension,
    ...BasicExtensions,
    TextColorExtension,
    FontSizeExtension,
    ...TableExtensions,
    ...TabViewExtensions,
    WJTagExtension,
];
