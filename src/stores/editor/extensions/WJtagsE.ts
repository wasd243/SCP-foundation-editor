// WJtagsE.ts keeps Wikijump/FTML-generated HTML from being dropped by TipTap's schema.
import { Extension } from "@tiptap/core";

import { createFootnoteSyncPlugin } from "./WJtags/FootnoteSyncE";
import {
    nativeAttributeTypes,
    preservedGlobalAttributes,
    WJHtmlPreserveExtensions,
} from "./WJtags/htmlPreserveE";

export const WJTagExtension = Extension.create({
    name: "wjTag",
    priority: 1,

    addGlobalAttributes() {
        return [
            {
                types: nativeAttributeTypes,
                attributes: Object.fromEntries(
                    preservedGlobalAttributes.map(name => [
                        name,
                        {
                            default: null,
                            parseHTML: (element: HTMLElement) =>
                                name === "hidden"
                                    ? (element.hasAttribute("hidden") ? "" : null)
                                    : element.getAttribute(name),
                            renderHTML: (attributes: Record<string, string | null>) =>
                                attributes[name] === null || attributes[name] === undefined
                                    ? {}
                                    : { [name]: attributes[name] },
                        },
                    ]),
                ),
            },
        ];
    },

    addExtensions() {
        return WJHtmlPreserveExtensions;
    },

    addProseMirrorPlugins() {
        return [
            createFootnoteSyncPlugin(),
        ];
    },
});
