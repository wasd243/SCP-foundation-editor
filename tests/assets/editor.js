import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";
import { StreamLanguage, syntaxHighlighting, HighlightStyle } from "@codemirror/language";
import { oneDark } from "@codemirror/theme-one-dark";
import { autocompletion } from "@codemirror/autocomplete";
import { keymap } from "@codemirror/view";
import { indentWithTab } from "@codemirror/commands";
import { Tag } from "@lezer/highlight";

// 1. 定义自定义高亮标签，防止 "Unknown highlighting tag" 报错
const customTags = {
    header: Tag.define(),
    strong: Tag.define(),
    em: Tag.define(),
    underline: Tag.define(),
    strikethrough: Tag.define(),
    wikiTag: Tag.define(),
    link: Tag.define(),
    hr: Tag.define(),
    rate: Tag.define(),
    right: Tag.define(),
    left: Tag.define(),
    center: Tag.define(),
    sup: Tag.define(),
    sub: Tag.define(),
    newline: Tag.define(),
    monosapace: Tag.define(),
    list1: Tag.define(),
    list2: Tag.define(),
    list3: Tag.define(),
    quote: Tag.define(),
    table: Tag.define(),
    table_header: Tag.define(),
    table_cell: Tag.define(),
    original_text: Tag.define(), // 用于原始文本
    image: Tag.define(), // 用于图片
    footnote: Tag.define(),
};

/**
 * 自定义 Wikidot 语法解析器
 */
const wikidotLanguage = StreamLanguage.define({
    token(stream) {
        // 标题
        if (stream.sol() && stream.match(/\++ /)) {
            stream.skipToEnd();
            return "header"; // 这里的字符串会被映射到 customTags.header
        }
        // 加粗
        if (stream.match(/\*\*.*?\*\*/)) return "strong";
        // 斜体
        if (stream.match(/\/\/.*?\/\//)) return "em";
        // 下划线
        if (stream.match(/__.*?__/)) return "underline";
        // 删除线
        if (stream.match(/--.*?--/)) return "strikethrough";
        // 上标
        if (stream.match(/\^\^.*?\^\^/)) return "sup";
        // 下标
        if (stream.match(/,,.*?,,/)) return "sub";
        // 链接
        if (stream.match(/\[https?:\/\/.*?\]/)) return "link";
        // 强制换行符
        if (stream.match(/\@\@\@\@/)) return "newline";
        // 英文等宽字体
        if (stream.match(/\{\{.*?\}\}/)) return "monosapace";
        // 原始文本
        if (stream.match(/\@\@.*?\@\@/)) {
            stream.skipToEnd();
            return "original_text"}
        // 无序列表
        if (stream.sol() && stream.match(/\*+ /)) {
            return "list1";
        }
        // 有序列表
        if (stream.sol() && stream.match(/#+ /)) {
            return "list2";
        }
        // 定义列表
        if (stream.sol() && stream.match(/\:.*?\:/)) {
            return "list3";
        }
        // 引用
        if (stream.sol() && stream.match(/>+ /)) {
            stream.skipToEnd();
            return "quote";
        }
        // 表格
        if (stream.match(/\|\|/)) {
        // 高亮竖线
            return "table";
        }
        if (stream.match(/\~/)) {
            return "table_header";
        }
        // 匹配普通表格行
        if (stream.sol() && stream.match(/\|\|(?!~)/)) {
            stream.skipToEnd();
            return "table_cell";
        }

        // 带有[[]]的注意需要放在标签前面，因为它也是以 [[ 开头的
        // ================================================================
        // 评分
        if (stream.match(/\[\[module rate\]\]/i)) return "rate";
        // 右对齐
        if (stream.match(/\[\[\>?\]\]/)) return "right";
        if (stream.match(/\[\[\/\>?\]\]/)) return "right";
        // 左对齐
        if (stream.match(/\[\[\<?\]\]/)) return "left";
        if (stream.match(/\[\[\/\<?\]\]/)) return "left";
        // 居中
        if (stream.match(/\[\[\=?\]\]/)) return "center";
        if (stream.match(/\[\[\/\=?\]\]/)) return "center";
        // 图片
        if (stream.match(/\[\[image.*?\]\]/)) return "image";
        // 脚注
        if (stream.match(/\[\[footnote\]\]/) || stream.match(/\[\[\/footnote\]\]/)) return "footnote";
        // ================================================================
        // Wikidot 标签
        if (stream.match(/\[\[.*?\]\]/)) return "wikiTag";
        // 分割线
        if (stream.sol() && stream.match(/^-{5,}$/)) return "hr";

        stream.next();
        return null;
    },
    // 关键：建立字符串标记与 Tag 对象的映射
    tokenTable: {
        "header": customTags.header,
        "strong": customTags.strong,
        "em": customTags.em,
        "underline": customTags.underline,
        "strikethrough": customTags.strikethrough,
        "wikiTag": customTags.wikiTag,
        "sup": customTags.sup,
        "sub": customTags.sub,
        "link": customTags.link,
        "hr": customTags.hr,
        "rate": customTags.rate,
        "right": customTags.right,
        "left": customTags.left,
        "center": customTags.center,
        "newline": customTags.newline,
        "monosapace": customTags.monosapace,
        "list1": customTags.list1,
        "list2": customTags.list2,
        "list3": customTags.list3,
        "quote": customTags.quote,
        "table": customTags.table,
        "table_header": customTags.table_header,
        "table_cell": customTags.table_cell,
        "original_text": customTags.original_text,
        "image": customTags.image,
        "footnote": customTags.footnote,
    }
});

// 2. 创建高亮样式映射，将标签转换为具体的 CSS 类名
const wikidotHighlightStyle = HighlightStyle.define([
    { tag: customTags.header, class: "cm-header" },
    { tag: customTags.strong, class: "cm-strong" },
    { tag: customTags.em, class: "cm-em" },
    { tag: customTags.underline, class: "cm-underline" },
    { tag: customTags.strikethrough, class: "cm-strikethrough" },
    { tag: customTags.wikiTag, class: "cm-wikiTag" },
    { tag: customTags.link, class: "cm-link" },
    { tag: customTags.hr, class: "cm-hr" },
    { tag: customTags.rate, class: "cm-rate" },
    { tag: customTags.right, class: "cm-right" },
    { tag: customTags.left, class: "cm-left" },
    { tag: customTags.center, class: "cm-center" },
    { tag: customTags.sup, class: "cm-sup" },
    { tag: customTags.sub, class: "cm-sub" },
    { tag: customTags.newline, class: "cm-newline" },
    { tag: customTags.monosapace, class: "cm-monosapace" },
    { tag: customTags.list1, class: "cm-list1" },
    { tag: customTags.list2, class: "cm-list2" },
    { tag: customTags.list3, class: "cm-list3" },
    { tag: customTags.quote, class: "cm-quote" },
    { tag: customTags.table, class: "cm-table" },
    { tag: customTags.table_header, class: "cm-table-header" },
    { tag: customTags.table_cell, class: "cm-table-cell" },
    { tag: customTags.original_text, class: "cm-original-text" },
    { tag: customTags.image, class: "cm-image" },
    { tag: customTags.footnote, class: "cm-footnote" },
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
import { wikidotCompletionSource } from "./completion.js";

// 3. 初始化编辑器
const startEditor = () => {
    const state = EditorState.create({
        doc: `[[include main-theme]]

+ 一级标题

**加粗文字**
//斜体文字//
__下划线文字__
--删除线文字--

[[footnote]]这是一个脚注[[/footnote]]

* 这是一个无序列表项
# 这是一个有序列表项
: 123 : 这是一个定义列表项

> 这是一个引用

[http://scp-wiki.wikidot.com SCP基金会]

||~表头1||~表头2||~表头3||
||单元格1||单元格2||单元格3||
||单元格4||单元格5||单元格6||

----

[[code type="python"]]
# 这是一个代码块
print("Hello, World!")
[[/code]]`,
        extensions: [
            // 将 customKeymap 放在 basicSetup 之前，确保优先级
            customKeymap,
            basicSetup,
            oneDark,
            wikidotLanguage,
            syntaxHighlighting(wikidotHighlightStyle),
            autocompletion({ override: [wikidotCompletionSource], selectOnOpen: true }),
            
            EditorView.updateListener.of((update) => {
                if (update.docChanged && window.py_bridge) {
                    window.py_bridge.on_code_changed(update.state.doc.toString());
                }
            }),

            EditorView.theme({
                "&": { height: "100%" },
                "&.cm-focused": { outline: "none" },
                ".cm-scroller": { 
                    fontFamily: "'Cascadia Code', 'Consolas', monospace",
                    lineHeight: "1.6"
                }
            })
        ]
    });

    new EditorView({
        state,
        parent: document.getElementById("editor-container")
    });
};

window.onload = startEditor;