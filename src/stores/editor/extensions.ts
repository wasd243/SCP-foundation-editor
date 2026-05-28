import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import StarterKit from "@tiptap/starter-kit";

import { BasicExtensions } from "./extensions/btnBasicE.ts";
import { CodeBlockLowlightExtension } from "./extensions/CodeE.ts";
import { DetailsExtension, DetailsSummaryExtension } from "./extensions/DetailsE.ts";
import { DetailsContentExtension } from "./extensions/DetailsContentE.ts";
import { FontSizeExtension } from "./extensions/FontSizeE.ts";
import { ImageExtension } from "./extensions/ImageE.ts";
import InvisibleCharacters, { ParagraphNode } from "@tiptap/extension-invisible-characters";
import { TableExtensions } from "./extensions/TableE.ts";
import { TabViewExtensions } from "./extensions/TabViewE.ts";
import { TextAlignExtension } from "./extensions/TextAlignE.ts";
import { TextColorExtension } from "./extensions/TextColorE.ts";
import { UserExtension } from "./extensions/User/UserE.ts";
import { UserWithImgExtension } from "./extensions/User/UserWithImgE.ts";
import { WJTagExtension } from "./extensions/WJtagsE.ts";

export const editorExtensions = [
    StarterKit.configure({
        codeBlock: false,
    }),
    Underline,
    Link.configure({
        openOnClick: false,
    }),
    ImageExtension.configure({
        inline: false,
        allowBase64: false,
    }),
    CodeBlockLowlightExtension,
    DetailsExtension,
    DetailsSummaryExtension,
    DetailsContentExtension,
    TextAlignExtension,
    InvisibleCharacters.configure({
        visible: true,
        builders: [new ParagraphNode()],
    }),
    ...BasicExtensions,
    TextColorExtension,
    FontSizeExtension,
    ...TableExtensions,
    ...TabViewExtensions,
    UserExtension,
    UserWithImgExtension,
    WJTagExtension,
];
