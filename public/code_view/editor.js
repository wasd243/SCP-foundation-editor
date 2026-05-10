/**
 * @file editor.js
 * @description SCP Foundation Wikidot Editor - Core Module
 * * --- LICENSE INFORMATION ---
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 * Copyright (c) 2026 Zichen Wang(wasd243)
 * * --- ATTRIBUTION & THIRD-PARTY COMPONENTS ---
 * 1. Editor Engine: CodeMirror 6 (MIT License) - © Marijn Haverbeke
 * 2. Syntax Patterns: ACS & AIM logic patterns are derived from the 
 * SCP Foundation community under CC BY-SA 3.0.
 * -------------------------------------------------------------------
 */
import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";
// Stream imports
import { syntaxHighlighting, HighlightStyle } from "@codemirror/language";
// Lezer imports
import { parser } from "./src/parser.js";
import { LRLanguage, LanguageSupport } from "@codemirror/language";
import { parseMixed } from "@lezer/common"
import { cssLanguage } from "@codemirror/lang-css"
import { htmlLanguage} from "@codemirror/lang-html"
import { styleTags, tags as t, Tag } from "@lezer/highlight";
import { foldNodeProp, foldInside } from "@codemirror/language";
// Other imports
import { foldGutter } from "@codemirror/language";
import { oneDark } from "@codemirror/theme-one-dark";
import { autocompletion } from "@codemirror/autocomplete";
import { keymap } from "@codemirror/view";
import { indentWithTab } from "@codemirror/commands";
// Import color preview extension and event handlers
import { colorPreviewExtension, setupColorPickerHandler } from "./component/color_preview.js";
import { wikidotColorExtension } from "./component/color_widgets.js";
// AST debug
import { syntaxTree } from "@codemirror/language";

// Initial content removed

// Define custom highlight tags to prevent "Unknown highlighting tag" errors
const customTags = {
    header: Tag.define(),
    strong: Tag.define(),
    em: Tag.define(),
    underline: Tag.define(),
    strikethrough: Tag.define(),
    module: Tag.define(), // MODULE
    html: Tag.define(), // HTML
    link: Tag.define(), // link 🔗
    hr: Tag.define(),
    rate: Tag.define(),
    right: Tag.define(),
    left: Tag.define(),
    center: Tag.define(),
    sup: Tag.define(),
    sub: Tag.define(),
    newline: Tag.define(),
    list1: Tag.define(),
    list2: Tag.define(),
    list3: Tag.define(),
    list4: Tag.define(),
    quote: Tag.define(),
    newline_defult: Tag.define(), // IMPORTANT new line defult defination
    code: Tag.define(), // for code blocks
    table: Tag.define(),
    table_header: Tag.define(),
    original_text: Tag.define(), // for original/raw text
    image: Tag.define(), // for images
    footnote: Tag.define(),
    footnote_block: Tag.define(), // for footnote blocks
    color: Tag.define(), 
    include: Tag.define(), // for [[include ...]] tags
    include_1: Tag.define(),
    include_2: Tag.define(),
    include_3: Tag.define(),
    num: Tag.define(),
    keyword: Tag.define(), // parameter
    scp_wiki: Tag.define(), // for specific theme tags
    div: Tag.define(), // for [[div ...]] tags
    tabview: Tag.define(), // for [[tabview]] tags
    tab: Tag.define(), // tabview enhancement
    acs: Tag.define(), // for ACS
    equal: Tag.define(), // for =
    line_up: Tag.define(), // for |
    size: Tag.define(), // for font-size tags
    aim: Tag.define(), // for AIM
    components: Tag.define(), // ATTRpathToken
    collapsible: Tag.define(), // for collapsible sections
    monospace: Tag.define(), // monospace text
    license: Tag.define(), // LICENSE
    note: Tag.define(), // note
    user: Tag.define(), // user
    Highlight: Tag.define(), // ATTR highlight
};

const wikidotParser = parser.configure({
    wrap: parseMixed((node, input) => {
    // When parser reaches ModuleContent node
        if (node.name === "ModuleContent") {
            const moduleBlock = node.node.parent;
            if (moduleBlock && moduleBlock.name === "ModuleBlock") {
                const openTag = moduleBlock.getChild("ModuleOpenTag");
                if (openTag) {
                    // Read full [[module CSS]] tag text directly
                    const tagText = input.read(openTag.from, openTag.to).toLowerCase();
                    
                    // Exclude native Wikidot modules
                    const nativeModules = ["rate", "listpages", "backlinks"];
                    if (nativeModules.some(m => tagText.includes(m))) {
                        return null;
                    }

                    // Enable nested CSS highlighting when tag contains css
                    if (tagText.includes("css")) {
                        return {
                            parser: cssLanguage.parser,
                            overlay: [{ from: node.from, to: node.to }]
                        };
                    }
                }
            }
        }
        
        // Same approach for HTML
        if (node.name === "HTMLContent") {
            return { 
                parser: htmlLanguage.parser,
                overlay: [{ from: node.from, to: node.to }] 
            };
        }
        return null;
    }),
    props: [
        styleTags({
            "Rate":                   customTags.rate,
            "IncludeOpen":            customTags.include,
            "IncludePart1":           customTags.include_1,
            "IncludePart2":           customTags.include_2,
            "IncludePart3":           customTags.include_3,
            "IncludeSimplePath":      customTags.include_2,
            "IncludeBar":             customTags.line_up,
            "IncludeValue":           customTags.keyword,
            "IncludeTagEnd":          customTags.include,
            "DivOpen":                customTags.div,
            "DivTagEnd":              customTags.div,
            "DivClose":               customTags.div,
            "CollapsibleOpen":        customTags.collapsible,
            "CollapsibleTagEnd":      customTags.collapsible,
            "CollapsibleClose":       customTags.collapsible,
            "CodeOpen":               customTags.code,
            "CodeTagEnd":             customTags.code,
            "CodeClose":              customTags.code,
            "UserOpen":               customTags.user,
            "UserTagEnd":             customTags.user,
            "FootnoteOpen":           customTags.footnote,
            "FootnoteTagEnd":         customTags.footnote,
            "FootnoteClose":          customTags.footnote,
            "LinkURL":                customTags.link,
            "ImageOpen":              customTags.image,
            "ImageTagEnd":            customTags.image,
            "TabViewOpenToken":       customTags.tabview,
            "TabViewCloseToken":      customTags.tabview,
            "TabOpenToken":           customTags.tab,
            "TabTagEnd":              customTags.tab,
            "TabCloseToken":          customTags.tab,
            "ModuleOpenToken":        customTags.module,
            "ModuleCloseToken":       customTags.module,
            "ModuleTagEnd":           customTags.module,
            "HTMLOpenToken":          customTags.html,
            "HTMLCloseToken":         customTags.html,
            "HTMLTagEnd":             customTags.html,
            "NoteOpenToken":          customTags.note,
            "NoteCloseToken":         customTags.note,
            "SizeOpenToken":          customTags.size,
            "SizeCloseToken":         customTags.size,
            "SizeTagEnd":             customTags.size,
            "AlignCenterOpenToken":   customTags.center,
            "AlignCenterCloseToken":  customTags.center,
            "AlignLeftOpenToken":     customTags.left,
            "AlignLeftCloseToken":    customTags.left,
            "AlignRightOpenToken":    customTags.right,
            "AlignRightCloseToken":   customTags.right,
            "SpanOpenToken":          customTags.div, // div and span share the same color
            "SpanCloseToken":         customTags.div,
            "SpanTagEnd":             customTags.div,

            // -------------------- table handling --------------------
            "TableTilde":             customTags.table_header,
            "TableBar":               customTags.table,
            // -------------------- table handling --------------------
            "List1":                  customTags.list1,
            "List2":                  customTags.list2,


            "FootnoteBlock":          customTags.footnote_block,


            // -------------------- common markers --------------------
            "Blockquote":             customTags.quote,
            "Hr":                     customTags.hr,
            "Title":                  customTags.header,
            "StrongText":             customTags.strong,
            "EmText":                 customTags.em,
            "UnderlineText":          customTags.underline,
            "StrikeText":             customTags.strikethrough,
            "SupText":                customTags.sup,
            "SubText":                customTags.sub,
            "Monospace":              customTags.monospace,
            "ForcedNewLine":          customTags.newline,
            "Original":               customTags.original_text,
            // -------------------- common markers --------------------
            "newline":                customTags.newline_defult,
            "attrPathToken":          customTags.components,
            "Equals":                 customTags.equal,
            "AttrValue":              customTags.Highlight,
        }),
        foldNodeProp.add({
            "DivBlock":         foldInside,
            "CollapsibleBlock": foldInside,
            "CodeBlock":        foldInside,
            "TabViewBlock":     foldInside,
            "TabBlock":         foldInside,
            "ModuleBlock":      foldInside,
            "IncludeBlock":     foldInside,
            "HTMLBlock":        foldInside,
            "NoteBlock":        foldInside,
            "SizeBlock":        foldInside,
            "AlignCenter":      foldInside,
            "AlignLeft":        foldInside,
            "AlignRight":       foldInside,
            "SpanBlock":        foldInside,
        })
    ]
});

/**
 * Custom Wikidot syntax parser
 */
const wikidotLanguage = LRLanguage.define({
  name: "wikidot",
  parser: wikidotParser,
  languageData: {
    commentTokens: { block: { open: "[[comment]]", close: "[[/comment]]" } }
  }
});


const wikidotHighlightStyle = HighlightStyle.define([
    { tag: customTags.header, class: "cm-header" },
    { tag: customTags.strong, class: "cm-strong" },
    { tag: customTags.em, class: "cm-em" },
    { tag: customTags.underline, class: "cm-underline" },
    { tag: customTags.strikethrough, class: "cm-strikethrough" },
    { tag: customTags.link, class: "cm-link" },
    { tag: customTags.hr, class: "cm-hr" },
    { tag: customTags.module, class: "cm-module"},
    { tag: customTags.html, class: "cm-html"},
    { tag: customTags.rate, class: "cm-rate" },
    { tag: customTags.right, class: "cm-right" },
    { tag: customTags.left, class: "cm-left" },
    { tag: customTags.center, class: "cm-center" },
    { tag: customTags.sup, class: "cm-sup" },
    { tag: customTags.sub, class: "cm-sub" },
    { tag: customTags.components, class: "cm-components"}, // ATTRLIST IMPORTANT
    { tag: customTags.keyword, class: "cm-keyword"}, // parameter
    { tag: customTags.newline, class: "cm-newline" },
    { tag: customTags.newline_defult, class: ""}, // IMPORTANT defult newline defination
    { tag: customTags.monospace, class: "cm-monospace"},
    { tag: customTags.list1, class: "cm-list1" },
    { tag: customTags.list2, class: "cm-list2" },
    { tag: customTags.list3, class: "cm-list3" },
    { tag: customTags.list4, class: "cm-list4" },
    { tag: customTags.num, class: "cm-num"},
    { tag: customTags.quote, class: "cm-quote"},
    { tag: customTags.code, class: "cm-code"},
    { tag: customTags.table, class: "cm-table" },
    { tag: customTags.table_header, class: "cm-table-header" },
    { tag: customTags.original_text, class: "cm-original-text" },
    { tag: customTags.image, class: "cm-image" },
    { tag: customTags.footnote, class: "cm-footnote" },
    { tag: customTags.footnote_block, class: "cm-footnote-block" },
    { tag: customTags.color, class: "cm-color" },
    { tag: customTags.include, class: "cm-include" },
    { tag: customTags.include_1, class: "cm-include-1"},
    { tag: customTags.include_2, class: "cm-include-2"},
    { tag: customTags.include_3, class: "cm-include-3"},
    { tag: customTags.scp_wiki, class: "cm-scp-wiki" },
    { tag: customTags.div, class: "cm-div" },
    { tag: customTags.tabview, class: "cm-tabview" },
    { tag: customTags.tab, class: "cm-tab" },
    { tag: customTags.acs, class: "cm-acs" },
    { tag: customTags.equal, class: "cm-equal" },
    { tag: customTags.line_up, class: "cm-line-up" },
    { tag: customTags.size, class: "cm-size" },
    { tag: customTags.aim, class: "cm-aim" },
    { tag: customTags.collapsible, class: "cm-collapsible" },
    { tag: customTags.note, class: "cm-note" },
    { tag: customTags.user, class: "cm-user" },
    { tag: customTags.Highlight, class: "cm-Highlight"},
]);

/**
 * Improved auto-continue list behavior for Wikidot syntax
 * Uses higher priority to override default behavior
 */
const customKeymap = keymap.of([
    {
        key: "Enter",
        run: (view) => {
            const state = view.state;
            const selection = state.selection.main;
            
            if (!selection.empty) return false;
            
            const line = state.doc.lineAt(selection.head);
            const cursorPos = selection.head - line.from;
            
            // Check whether cursor is at (or near) line end
            const isAtEndOfLine = cursorPos >= line.text.length - 1;
            
            if (!isAtEndOfLine) {
                // If cursor is not at line end, fall back to default behavior
                return false;
            }
            
            // Wikidot list syntax: * for unordered, # for ordered lists
            // Match * or # at line start, followed by required whitespace
            const listMatch = line.text.match(/^([*#])\s+/);
            const list3Match = line.text.match(/^(:.*?:)\s+/); // definition list match
            
            if (listMatch || list3Match) {
                const listMarker = listMatch ? listMatch[1] : list3Match[1]; // * or # or :
                
                // Check whether Enter was pressed on an empty list item
                const contentAfterMarker = line.text.substring(listMarker.length + 1).trim();
                const isListItemEmpty = contentAfterMarker === '';
                
                if (isListItemEmpty) {
                    // Empty list item: remove marker from current line
                    view.dispatch({
                        changes: { 
                            from: line.from, 
                            to: line.to, 
                            insert: "" 
                        },
                        selection: { anchor: line.from }
                    });
                    return true;
                } else {
                    // Non-empty list item: insert new line and continue marker
                    const newLineContent = `\n${listMarker} `;
                    
                    view.dispatch({
                        changes: { 
                            from: selection.head, 
                            to: selection.head, 
                            insert: newLineContent 
                        },
                        selection: { anchor: selection.head + newLineContent.length }
                    });
                    return true;
                }
            }
            
            return false;
        }
    },
    indentWithTab
]);

/**
 * Auto Completion
 */
import { wikidotCompletionSource } from "./component/completion.js";
import { foldEffect } from "@codemirror/language/dist/index.js";

// 3. Initialize editor
const startEditor = () => {
    const state = EditorState.create({
        doc: "",
        extensions: [
            // Disable line wrapping
            EditorView.lineWrapping,
            // Put customKeymap before basicSetup to ensure priority
            customKeymap,
            basicSetup,
            oneDark,
            // Custom Wikidot syntax
            wikidotLanguage,
            syntaxHighlighting(wikidotHighlightStyle),
            // Add Wikidot color tag extension first
            wikidotColorExtension,
            // Then add generic color preview extension
            colorPreviewExtension,
            autocompletion({ override: [wikidotCompletionSource], selectOnOpen: true }),
            
            // Web version: local-storage auto-save removed
            EditorView.updateListener.of((update) => {
                if (update.docChanged) {
                    const content = update.state.doc.toString();
                    
                    // Send latest content to userscript via postMessage
                    window.parent.postMessage({
                        type: 'h2o2-update',
                        payload: content
                    }, '*'); 
                }
            }),

            EditorView.theme({
                "&": { height: "100%" },
                "&.cm-focused": { outline: "none" },
                ".cm-scroller": { 
                    fontFamily: "'Cascadia Code', 'Consolas', 'Monaco', 'Courier New', monospace",
                    lineHeight: "1.6",
                    fontSize: "14px"
                },
                // Basic styles for color preview
                ".cm-color-preview": {
                    display: "inline-block",
                    width: "12px",
                    height: "12px",
                    margin: "0 4px 0 0",
                    border: "1px solid #555",
                    borderRadius: "2px",
                    backgroundColor: "var(--color-value, #ccc)",
                    verticalAlign: "middle",
                    cursor: "pointer",
                    transition: "transform 0.2s ease, border-color 0.2s ease"
                },
                ".cm-color-preview:hover": {
                    transform: "scale(1.1)",
                    borderColor: "#888"
                },
                // Wikidot color text style
                ".cm-wikidot-colored-text": {
                    fontWeight: "normal!important",
                }
            })
        ]
    });

    const editorView = new EditorView({
        state,
        parent: document.getElementById("editor-container"),
        viewportMargin: 2000
    });

    // AST debug
    // Added after editorView is created in startEditor:
    window._debugAST = () => {
        const tree = syntaxTree(editorView.state);
        tree.cursor().iterate(node => {
            console.log(node.name, editorView.state.sliceDoc(node.from, node.to));
        });
    };
    
    // Set up color picker event handling
    setupColorPickerHandler(editorView);
    
    // Expose instance globally for index.html button actions
    window.editorInstance = editorView;

    return editorView;
};

// Listen for init/re-sync requests from the userscript
window.addEventListener('message', (event) => {
    // Allow messages from all Wikidot sub-sites
    const isWikidot = event.origin.endsWith('wikidot.com');
    
    if (!isWikidot) return;
    // Ignore unrelated messages (e.g., noisy extension injections)
    if (!event.data || event.data.type !== 'h2o2-init') return;
    
    console.log("H2O2 Web: Successfully received initial content from Wikidot textarea.");
    
    const view = window.editorInstance;
    if (view) {
        // Replace full editor content with received textarea payload
        view.dispatch({
            changes: { 
                from: 0, 
                to: view.state.doc.length, 
                insert: event.data.payload || ''
            }
        });
    } else {
        console.warn("H2O2 Web: Received data, but editor instance is not ready yet.");
    }
});

// Export editor instance for other scripts
window.WikidotEditor = {
    startEditor,
    // Additional public APIs can be added here
};

// Start editor after DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startEditor);
} else {
    startEditor();
}
