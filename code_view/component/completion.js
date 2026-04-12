// completion.js
export const wikidotCompletionSource = (context) => {

    // ====== 新增：判定当前上下文范围 ======
    // 获取从文档开头到当前光标的所有文本
    const textBefore = context.state.sliceDoc(0, context.pos);
    
    // 判定是否在 CSS 内：比较最后一次开启和关闭标签的位置
    const lowerText = textBefore.toLowerCase();
    const lastCssOpen = lowerText.lastIndexOf('[[module css]]');
    const lastCssClose = lowerText.lastIndexOf('[[/module]]');
    const inCSS = lastCssOpen > lastCssClose;

    // 判定是否在 HTML 内
    const lastHtmlOpen = textBefore.toLowerCase().lastIndexOf('[[html]]');
    const lastHtmlClose = textBefore.toLowerCase().lastIndexOf('[[/html]]');
    const inHTML = lastHtmlOpen > lastHtmlClose;

    // 如果在 CSS 内部，拦截并专属补全
    if (inCSS) {
        let word = context.matchBefore(/[a-zA-Z-]+/);
        if (!word || (word.from === word.to && !context.explicit)) return null;
        return {
            from: word.from,
            options: [
                // 往这里加 CSS 词库
                { label: "color", type: "property", apply: "color: ;", detail: "文本颜色" },
                { label: "background-color", type: "property", apply: "background-color: ;", detail: "背景色" },
                { label: "display", type: "property", apply: "display: flex;", detail: "弹性布局" },
                { label: "border", type: "property", apply: "border: 1px solid #fff;", detail: "边框" },
            ],
            filter: true
        };
    }

    // 如果在 HTML 内部，拦截并专属补全
    if (inHTML) {
        let word = context.matchBefore(/<\/?[a-zA-Z0-9-]*/);
        if (!word || (word.from === word.to && !context.explicit)) return null;
        return {
            from: word.from,
            options: [
                { label: "<div>", type: "keyword", apply: "<div>\n\n</div>", detail: "块级元素" },
                { label: "<span>", type: "keyword", apply: "<span></span>", detail: "行内元素" },
                { label: "<style>", type: "keyword", apply: "<style>\n\n</style>", detail: "样式表" },
                { label: "class", type: "property", apply: "class=\"\"", detail: "类名" },
            ],
            filter: true
        };
    }
    // ====== 新增判定结束 ======

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
                label: "[[size ",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    const text = "[[size ]]\n\n[[/size";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[size ".length } // 光标放在 size 后面
                    });
                }
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
                label: "[[tabview",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 tabview 标签，光标放在标签名后
                    const text = "[[tabview]]\n[[/tabview";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[tabview".length } // 光标放在标签名之后
                    });
                },
                detail: "标签页"
            },
            {
                label: "[[tab", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // 插入 tab 标签，光标放在tab
                    const text = "[[tab ]]\n[[/tab";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[tab ".length } // 光标放在tab
                    });
                }, 
                detail: "tab" 
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
                label: "[[include :scp-wiki-cn:component:",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 component 标签，光标放在后面
                    const text = "[[include :scp-wiki-cn:component:";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // 光标放在标签名之后
                    });
                },
                detail: "组件"
            },
            {
                label: "[[include :scp-wiki-cn:component:acs-animation",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 acs-animation 类名
                    const text = "[[include :scp-wiki-cn:component:acs-animation";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "acs-animation"
            },
            {
                label: "[[include :scp-wiki-cn:component:anomaly-class-bar-source",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 anomaly-class-bar-source 类名
                    const text = "[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number=SCP-CN-XXXX\n|clearance= \n|container-class= \n|disruption= \n|risk-class= \n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + 80, head: from + 91 } // 光标放在标签名之后
                    });
                },
                detail: "ACS",
                source: "10000000000000000000000000000000000000000000000000000000000000000000000000000000000000" // 设定较高的优先级,
            },
            {
                label: "[[include :scp-wiki-cn:component:advanced-information-methodaology",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 advanced-information-methodaology 类名
                    const text = "[[include :scp-wiki-cn:component:advanced-information-methodaology\n|lang=cn\n|XXXX=SCP-XXXX\n|lv=等级\n|cc= \n|dc= \n|site= \n|dir= \n|head= \n|mtf= \n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + 87, head: from + 91 }
                    });
                }
            },
            {
                label: "[[include :scp-wiki-cn:component:license-box",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 license-box 类名
                    const text = "[[include :scp-wiki-cn:component:license-box\n|lang=cn\n|author= \n]]\n=====\n> 文件名：\n> 图像名： \n> 图像作者： \n> 授权协议： \n> 来源链接：\n=====\n[[include :scp-wiki-cn:component:license-end";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + 81 }
                    });
                }
            },
            {
                label: "[[span",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 span 标签，光标放在属性位置
                    const text = "[[span class=\"\"]]\n\n[[/span";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[span class=\"".length } // 光标放在 class 属性的双引号之间
                    });
                }
            },
            {
                label: "[[collapsible]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 collapsible 标签，光标放在标签名后
                    const text = "[[collapsible show=\"+\" hide=\"-\"]]\n[[/collapsible";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[collapsible".length + 8 } // 光标放在标签名之后
                    });
                },
                detail: "可折叠内容"
            },
            {
                label: "[[note",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 note
                    const text = "[[note]]\n\n[[/note";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[note]]\n".length }
                    });
                },
                detail: "笔记"
            },
            {
                label: "[[user",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 user
                    const text = "[[*user "
                    view.dispatch({
                        changes: { from, to, insert: text},
                        selection: { anchor: from + "[[#user ".length }
                    });
                },
                detail: "用户头像"
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
            {
                label: "[[module css]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 css 模块，光标放在标签内部
                    const text = "[[module css]]\n\n[[/module";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[module css".length + 2 } // 光标放在标签内部
                    });
                },
                detail: "CSS 模块"
            },
            {
                label: "[[html]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入 html 模块，光标放在标签内部
                    const text = "[[html]]\n\n[[/html";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[html".length + 2 } // 光标放在标签内部
                    });
                },
                detail: "HTML 模块"

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
                label: "[[include component:image-block",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 导入插图块
                    const text = "[[include component:image-block\n|name= \n|caption= \n|width= \n|height= \n|align= ";
                    const selectFrom = from + "[[include component:image-block\n|name=".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom } // 光标
                    });
                }, 
                detail: "插图块"
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
            {
                label: "[[footnoteblock]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // 插入脚注块标签，选中脚注块内容
                    const text = "[[footnoteblock";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "脚注块"
            },
        ],
        filter: true 
    };
};
