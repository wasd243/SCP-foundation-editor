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
// Stream导入
import { syntaxHighlighting, HighlightStyle } from "@codemirror/language";
// Lezer导入
import { parser } from "./src/parser.js";
import { LRLanguage, LanguageSupport } from "@codemirror/language";
import { parseMixed } from "@lezer/common"
import { cssLanguage } from "@codemirror/lang-css"
import { htmlLanguage} from "@codemirror/lang-html"
import { styleTags, tags as t, Tag } from "@lezer/highlight";
import { foldNodeProp, foldInside } from "@codemirror/language";
// 其他导入
import { foldGutter } from "@codemirror/language";
import { oneDark } from "@codemirror/theme-one-dark";
import { autocompletion } from "@codemirror/autocomplete";
import { keymap } from "@codemirror/view";
import { indentWithTab } from "@codemirror/commands";
// 导入颜色预览扩展和事件处理函数
import { colorPreviewExtension, setupColorPickerHandler } from "./component/color_preview.js";
import { wikidotColorExtension } from "./component/color_widgets.js";
// AST测试
import { syntaxTree } from "@codemirror/language";

// 初始化内容 已删除

// 定义自定义高亮标签，防止 "Unknown highlighting tag" 报错
const customTags = {
    header: Tag.define(),
    strong: Tag.define(),
    em: Tag.define(),
    underline: Tag.define(),
    strikethrough: Tag.define(),
    module: Tag.define(), // MODULE
    html: Tag.define(), // HTML
    link: Tag.define(), // 链接🔗
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
    code: Tag.define(), // 用于代码块
    table: Tag.define(),
    table_header: Tag.define(),
    original_text: Tag.define(), // 用于原始文本
    image: Tag.define(), // 用于图片
    footnote: Tag.define(),
    footnote_block: Tag.define(), // 用于脚注块
    color: Tag.define(), 
    include: Tag.define(), // 用于 [[include ...]] 标签
    include_1: Tag.define(),
    include_2: Tag.define(),
    include_3: Tag.define(),
    num: Tag.define(),
    keyword: Tag.define(), // 参数
    scp_wiki: Tag.define(), // 用于特定的主题标签
    div: Tag.define(), // 用于 [[div ...]] 标签
    tabview: Tag.define(), // 用于 [[tabview]] 标签
    tab: Tag.define(), // tabview增强
    acs: Tag.define(), // 用于ACS
    equal: Tag.define(), // 用于 = 号
    line_up: Tag.define(), // 用于|
    size: Tag.define(), // 用于字体大小标签
    aim: Tag.define(), // 用于AIM
    components: Tag.define(), // ATTRpathToken
    collapsible: Tag.define(), // 用于可折叠内容
    monospace: Tag.define(), // 等宽字
    license: Tag.define(), // LICENSE
    note: Tag.define(), // note
    user: Tag.define(), // user
    Highlight: Tag.define(), // ATTR highlight
};

const wikidotParser = parser.configure({
    wrap: parseMixed((node, input) => {
    // 当解析器走到 ModuleContent 节点时
        if (node.name === "ModuleContent") {
            const moduleBlock = node.node.parent;
            if (moduleBlock && moduleBlock.name === "ModuleBlock") {
                const openTag = moduleBlock.getChild("ModuleOpenTag");
                if (openTag) {
                    // 直接读取整个 [[module CSS]] 标签的文本
                    const tagText = input.read(openTag.from, openTag.to).toLowerCase();
                    
                    // 排除原生的 Wikidot 模块
                    const nativeModules = ["rate", "listpages", "backlinks"];
                    if (nativeModules.some(m => tagText.includes(m))) {
                        return null;
                    }

                    // 只要标签里写了 css，就开启 CSS 嵌套高亮
                    if (tagText.includes("css")) {
                        return {
                            parser: cssLanguage.parser,
                            overlay: [{ from: node.from, to: node.to }]
                        };
                    }
                }
            }
        }
        
        // HTML 同理
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
            "SpanOpenToken":          customTags.div, // 这里div和span的颜色一样
            "SpanCloseToken":         customTags.div,
            "SpanTagEnd":             customTags.div,

            // ——————————————————————————表格操作——————————————————————————
            "TableTilde":             customTags.table_header,
            "TableBar":               customTags.table,
            // ——————————————————————————表格操作——————————————————————————
            "List1":                  customTags.list1,
            "List2":                  customTags.list2,


            "FootnoteBlock":          customTags.footnote_block,


            // ——————————————————————————常用标记——————————————————————————
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
            // ——————————————————————————常用标记——————————————————————————
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
 * 自定义 Wikidot 语法解析器
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
    { tag: customTags.keyword, class: "cm-keyword"}, // 参数
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
 * 改进的自动延续列表逻辑 - 针对Wikidot语法
 * 使用更高优先级确保覆盖默认行为
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
            
            // 检查光标是否在行末（或者接近行末）
            const isAtEndOfLine = cursorPos >= line.text.length - 1;
            
            if (!isAtEndOfLine) {
                // 如果光标不在行末，让默认行为处理（比如在行中间换行）
                return false;
            }
            
            // Wikidot列表语法：单个*表示无序列表，单个#表示有序列表
            // 匹配行首的 * 或 #，后面必须跟空格
            const listMatch = line.text.match(/^([*#])\s+/);
            const list3Match = line.text.match(/^(:.*?:)\s+/); // 定义列表匹配
            
            if (listMatch || list3Match) {
                const listMarker = listMatch ? listMatch[1] : list3Match[1]; // * 或 # 或 :
                
                // 检查是否在空列表项上按回车
                const contentAfterMarker = line.text.substring(listMarker.length + 1).trim();
                const isListItemEmpty = contentAfterMarker === '';
                
                if (isListItemEmpty) {
                    // 空列表项：删除当前行的列表标记
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
                    // 非空列表项：插入新行并延续列表标记
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
 * 自动补全配置
 */
import { wikidotCompletionSource } from "./component/completion.js";
import { foldEffect } from "@codemirror/language/dist/index.js";

// 3. 初始化编辑器
const startEditor = () => {
    const state = EditorState.create({
        doc: "",
        extensions: [
            // 将 customKeymap 放在 basicSetup 之前，确保优先级
            customKeymap,
            basicSetup,
            oneDark,
            // 自定义wikidot语法
            wikidotLanguage,
            syntaxHighlighting(wikidotHighlightStyle),
            // 先添加Wikidot颜色标签扩展
            wikidotColorExtension,
            // 再添加普通颜色预览扩展
            colorPreviewExtension,
            autocompletion({ override: [wikidotCompletionSource], selectOnOpen: true }),
            
            // Web版本：删除本地存储自动保存功能
            EditorView.updateListener.of((update) => {

                if (update.docChanged) {
                    const content = update.state.doc.toString();
                    
                    if (window.pyBridge) {
                        window.pyBridge.on_code_changed(content);
                    }
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
                // 为颜色预览添加一些基本样式
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
                // Wikidot颜色文本样式
                ".cm-wikidot-colored-text": {
                    fontWeight: "normal!important",
                }
            })
        ]
    });

    const editorView = new EditorView({
        state,
        parent: document.getElementById("editor-container"),
        viewportMargin: Infinity
    });

    // AST测试
    // 在 startEditor 里，editorView 创建之后加：
    window._debugAST = () => {
        const tree = syntaxTree(editorView.state);
        tree.cursor().iterate(node => {
            console.log(node.name, editorView.state.sliceDoc(node.from, node.to));
        });
    };
    
    // 设置颜色选择器事件处理
    setupColorPickerHandler(editorView);
    
    // 将实例挂载到全局，方便 index.html 的按钮调用
    window.editorInstance = editorView;

    return editorView;
};

// 导出编辑器实例供其他脚本使用
window.WikidotEditor = {
    startEditor,
    // 可以添加其他公共API
};

// 当DOM加载完成后启动编辑器
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startEditor);
} else {
    startEditor();
}
window.startEditor = startEditor; // 直接挂载到全局，方便 html 调用