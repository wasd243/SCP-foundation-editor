// completion.js
export const wikidotCompletionSource = (context) => {
    // 查找光标前最近的 "[["
    let before = context.matchBefore(/\[\[[\w\s:]*/);
    let atMatch = context.matchBefore(/^\@+/);
    let tableMatch = context.matchBefore(/\|\|.*?/);
    // 匹配引号内的内容（不包括引号本身）
    let classMatch = context.matchBefore(/(?<=")[^"]*$|(?<=')[^']*$/);

    // 如果光标前是 "@@@@"，则提供强制换行符的补全选项
    if (atMatch && (atMatch.from !== atMatch.to || context.explicit)) {
        return {
            from: atMatch.from,
            options: [
                { 
                    label: "@@@@", 
                    type: "keyword", 
                    apply: "@@@@", 
                    detail: "强制换行 / 原始文本" 
                },
                { 
                    label: "@@...@@", 
                    type: "keyword", 
                    apply: (view, completion, from, to) => {
                        // 插入文本并将光标放在中间
                        const text = "@@Your text here@@";
                        const selectFrom = from + "@@".length
                        const selectTo = selectFrom + "Your text here".length
                        view.dispatch({
                            changes: { from, to, insert: text },
                            selection: { 
                                anchor: selectFrom,
                                head: selectTo } // 光标放在 @@ 之后
                        });
                    }, 
                    detail: "原始文本" 
                }
            ],
            filter: true
        };
    }

    // 如果光标前是表格语法，提供表格相关的补全选项
    if (tableMatch && (tableMatch.from !== tableMatch.to || context.explicit)) {
        return {
            from: tableMatch.from,
            options: [
                { 
                    label: "|| Header 1 || Header 2 ||", 
                    type: "keyword", 
                    apply: (view, completion, from, to) => {
                        // 插入表头行并将光标放在第一个表头位置
                        const text = "||~Header 1||~Header 2||";
                        view.dispatch({
                            changes: { from, to, insert: text },
                            selection: { anchor: from + 3 } // 光标放在 ||~ 之后
                        });
                    }, 
                    detail: "表头行" 
                },
                { 
                    label: "|| Cell 1 || Cell 2 ||", 
                    type: "keyword", 
                    apply: (view, completion, from, to) => {
                        // 插入表格行并将光标放在第一个单元格位置
                        const text = "||Cell 1||Cell 2||";
                        view.dispatch({
                            changes: { from, to, insert: text },
                            selection: { anchor: from + 2 } // 光标放在 || 之后
                        });
                    }, 
                    detail: "表格行" 
                }
            ],
            filter: true
        };
    }

    // 如果光标前是 class="，提供常见的 CSS 类名补全选项
    if (classMatch && (classMatch.from !== classMatch.to || context.explicit)) {
    // 提供 class 值的补全
    return {
        from: classMatch.from,
        options: [
             // 版式用div自动补全
             // ========================================================
            { 
                label: "[[div ", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    const text = "[[div class=\"\"]]\n\n[[/div";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[div class=\"".length }
                    });
                }, 
                detail: "容器" 
            },
            {
                label: "blockquote",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 blockquote 类名
                    const text = "blockquote";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "blockquote"
            },
            {
                label: "notation",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "notation";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "notation"
            },
            {
                label: "jotting",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "jotting";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "jotting"
            },
            {
                label: "modal",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "modal";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "modal"
            },
            {
                label: "smallmodal",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "smallmodal";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "smallmodal"
            },
            {
                label: "papernote",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "papernote";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "papernote"
            },
            {
                label: "floatbox",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "floatbox";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "floatbox"
            },
            {
                label: "document",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "document";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "document"
            },
            {
                label: "darkdocument",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "darkdocument";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "darkdocument"
            },
            {
                label: "raisa_memo",
                type: "constant",
                apply: (view, completion, from, to) => {
                    const text = "raisa_memo";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "raisa_memo"
            },
            // ========================================================
        ],
        filter: true
    };
}

    // 如果没搜到 "[["，或者搜索结果不是以 "[[" 开始，则不触发
    if (!before || before.from == before.to && !context.explicit) return {
        from: context.pos,
        options: []
    };

    return {
        from: before.from,
        options: [
            // 常见标签
            { 
                label: "[[div ", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    const text = "[[div class=\"\"]]\n\n[[/div";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[div class=\"".length }
                    });
                }, 
                detail: "容器" 
            },
            { 
                label: "[[include ", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    const text = "[[include ";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // 光标放在标签名之后
                    });
                }, 
                detail: "引用页面" 
            },
            {
                label: "[[include :scp-wiki",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入分会标签，光标放在后面
                    const text = "[[include :scp-wiki";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // 光标放在标签名之后
                    });
                },
                detail: "SCP-Wiki"
            },
            {
                label: "[[include :scp-wiki-cn",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 theme 标签，光标放在后面
                    const text = "[[include :scp-wiki-cn:theme:";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // 光标放在标签名之后
                    });
                },
                detail: "版式"
            },
            {
                label: "[[span",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 span 标签，光标放在属性位置
                    const text = "[[span class=\"\"";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[span class=\"".length } // 光标放在 class 属性的双引号之间
                    });
                }
            },
            { 
                label: "[[module ", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入 module 标签，光标放在模块名位置
                    const text = "[[module ";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // 光标放在标签名之后
                    });
                }, 
                detail: "功能组件" 
            },

            // 更多 Wikidot 标签可以在这里添加
            { 
                label: "[[module rate]]", 
                type: "function", 
                apply: (view, completion, from, to) => {
                    // 插入 rate 模块，光标放在标签内部
                    const text = "[[module rate";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length + 2 }
                    });
                }, 
                detail: "评分模块" 
            },
            { 
                label: "[[code]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入代码块，光标放在 type="" 的双引号之间
                    const text = "[[code type=\"\"]]\n\n[[/code";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[code type=\"".length } // 光标放在双引号之间
                    });
                }, 
                detail: "代码块" 
            },
            { 
                label: "[[>]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入右对齐标签，选中内容区域
                    const text = "[[>]]\n对齐内容\n[[/>";
                    const selectFrom = from + "[[>]]\n".length;
                    const selectTo = selectFrom + "对齐内容".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "右对齐" 
            },
            { 
                label: "[[<]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入左对齐标签，选中内容区域
                    const text = "[[<]]\n对齐内容\n[[/<";
                    const selectFrom = from + "[[<]]\n".length;
                    const selectTo = selectFrom + "对齐内容".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "左对齐" 
            },
            { 
                label: "[[=]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入居中标签，选中内容区域
                    const text = "[[=]]\n居中内容\n[[/=";
                    const selectFrom = from + "[[=]]\n".length;
                    const selectTo = selectFrom + "居中内容".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "居中" 
            },
            { 
                label: "[[image ", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入图片标签，光标放在属性位置
                    const text = "[[image ";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // 光标放在标签名之后
                    });
                }, 
                detail: "图片" 
            },
            { 
                label: "[[footnote]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入脚注标签，选中脚注内容
                    const text = "[[footnote]]这是一条脚注[[/footnote";
                    const selectFrom = from + "[[footnote]]".length;
                    const selectTo = selectFrom + "这是一条脚注".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "脚注" 
            },
        ],
        filter: true 
    };
};
