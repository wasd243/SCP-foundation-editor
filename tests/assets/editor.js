import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";
import { StreamLanguage, syntaxHighlighting, HighlightStyle } from "@codemirror/language";
import { oneDark } from "@codemirror/theme-one-dark";
import { autocompletion } from "@codemirror/autocomplete";
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
    newline: Tag.define()
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
        // ================================================================
        // Wikidot 标签
        if (stream.match(/\[\[.*?\]\]/)) return "wikiTag";
        // 分隔线
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
        "newline": customTags.newline
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
    {tag: customTags.left, class: "cm-left" },
    {tag: customTags.center, class: "cm-center" },
    {tag: customTags.sup, class: "cm-sup" },
    {tag: customTags.sub, class: "cm-sub" },
    {tag: customTags.newline, class: "cm-newline" }
]);

/**
 * 自动补全配置
 */
const wikidotCompletionSource = (context) => {
    // 查找光标前最近的 "[["
    let before = context.matchBefore(/\[\[[\w\s]*/);
    let atMatch = context.matchBefore(/^\@+/);

    // 如果光标前是 "@@@@"，则提供强制换行符的补全选项
    if (atMatch && (atMatch.from !== atMatch.to || context.explicit)) {
        return {
            from: atMatch.from,
            options: [
                { label: "@@@@", type: "keyword", apply: "@@@@", detail: "强制换行 / 原始文本" }
            ],
            filter: true
        };
    }
    
    // 如果没搜到 "[["，或者搜索结果不是以 "[[" 开始，则不触发
    if (!before || before.from == before.to && !context.explicit) return {
        from: context.pos,
        options: [
            // 这里可以提供一些全局的补全选项，或者直接返回空数组
        ]
    };

    return {
        from: before.from,
        options: [
            // 常见标签
            { label: "[[include ", type: "keyword", detail: "引用页面" },
            { label: "[[div ", type: "keyword", detail: "容器" },
            { label: "[[module ", type: "keyword", detail: "功能组件" },

            // 更多 Wikidot 标签可以在这里添加
            // 注意这里不需要后面两个]]，因为用户输入[[后会自动补全]]，我们只需要提供标签的前半部分
            { label: "[[module rate]]", type: "function", apply: "[[module rate", detail: "评分模块" },
            { label: "[[code]]", type: "keyword", apply: "[[code]]\n\n[[/code", detail: "代码块" },
            { label: "[[>]]", type: "keyword", apply: "[[>]]\n\n[[/>", detail: "右对齐" },
            { label: "[[<]]", type: "keyword", apply: "[[<]]\n\n[[/<", detail: "左对齐" },
            { label: "[[=]]", type: "keyword", apply: "[[=]]\n\n[[/=", detail: "居中" }
        ],
        // 允许根据输入内容进行有效过滤
        filter: true 
    };
};

// 3. 初始化编辑器
const startEditor = () => {
    const state = EditorState.create({
        doc: "[[include main-theme]]\n\n+ 一级标题\n\n**加粗文字**\n//斜体文字//\n__下划线文字__\n--删除线文字--\n\n[http://scp-wiki.wikidot.com SCP基金会]\n\n----\n\n[[code]]\n  // 纯 Wikidot 环境\n[[/code]]",
        extensions: [
            basicSetup,
            oneDark,
            wikidotLanguage,
            syntaxHighlighting(wikidotHighlightStyle), // 应用自定义高亮映射
            autocompletion({ override: [wikidotCompletionSource] }),
            
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