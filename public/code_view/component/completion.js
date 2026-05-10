// completion.js
export const wikidotCompletionSource = (context) => {

    // ====== Added: detect current context range ======
    // Read all text from start of document to current cursor
    const textBefore = context.state.sliceDoc(0, context.pos);
    
    // Determine whether cursor is inside CSS: compare latest open/close tags
    const lowerText = textBefore.toLowerCase();
    const lastCssOpen = lowerText.lastIndexOf('[[module css]]');
    const lastCssClose = lowerText.lastIndexOf('[[/module]]');
    const inCSS = lastCssOpen > lastCssClose;

    // Determine whether cursor is inside HTML
    const lastHtmlOpen = textBefore.toLowerCase().lastIndexOf('[[html]]');
    const lastHtmlClose = textBefore.toLowerCase().lastIndexOf('[[/html]]');
    const inHTML = lastHtmlOpen > lastHtmlClose;

    // If inside CSS, provide CSS-only completion
    if (inCSS) {
        let word = context.matchBefore(/[a-zA-Z-]+/);
        if (!word || (word.from === word.to && !context.explicit)) return null;
        return {
            from: word.from,
            options: [
                // Add CSS suggestions here
                { label: "color", type: "property", apply: "color: ;", detail: "text color" },
                { label: "background-color", type: "property", apply: "background-color: ;", detail: "background color" },
                { label: "display", type: "property", apply: "display: flex;", detail: "flex layout" },
                { label: "border", type: "property", apply: "border: 1px solid #fff;", detail: "border" },
            ],
            filter: true
        };
    }

    // If inside HTML, provide HTML-only completion
    if (inHTML) {
        let word = context.matchBefore(/<\/?[a-zA-Z0-9-]*/);
        if (!word || (word.from === word.to && !context.explicit)) return null;
        return {
            from: word.from,
            options: [
                { label: "<div>", type: "keyword", apply: "<div>\n\n</div>", detail: "block element" },
                { label: "<span>", type: "keyword", apply: "<span></span>", detail: "inline element" },
                { label: "<style>", type: "keyword", apply: "<style>\n\n</style>", detail: "stylesheet" },
                { label: "class", type: "property", apply: "class=\"\"", detail: "class name" },
            ],
            filter: true
        };
    }
    // ====== End added context detection ======

    // Find nearest "[[" before cursor
    let before = context.matchBefore(/\[\[[\w\s:]*/);
    let atMatch = context.matchBefore(/^\@+/);
    let tableMatch = context.matchBefore(/\|\|.*?/);
    // Match content inside quotes (excluding quote chars)
    let classMatch = context.matchBefore(/(?<=")[^"]*$|(?<=')[^']*$/);

    // If token before cursor is "@@@@", suggest forced line-break options
    if (atMatch && (atMatch.from !== atMatch.to || context.explicit)) {
        return {
            from: atMatch.from,
            options: [
                { 
                    label: "@@@@", 
                    type: "keyword", 
                    apply: "@@@@", 
                    detail: "forced line break / raw text" 
                },
                { 
                    label: "@@...@@", 
                    type: "keyword", 
                    apply: (view, completion, from, to) => {
                        // Insert text and place cursor in the middle
                        const text = "@@Your text here@@";
                        const selectFrom = from + "@@".length
                        const selectTo = selectFrom + "Your text here".length
                        view.dispatch({
                            changes: { from, to, insert: text },
                            selection: { 
                                anchor: selectFrom,
                                head: selectTo } // cursor after opening @@
                        });
                    }, 
                    detail: "raw text" 
                }
            ],
            filter: true
        };
    }

    // If table syntax is detected, provide table completions
    if (tableMatch && (tableMatch.from !== tableMatch.to || context.explicit)) {
        return {
            from: tableMatch.from,
            options: [
                { 
                    label: "|| Header 1 || Header 2 ||", 
                    type: "keyword", 
                    apply: (view, completion, from, to) => {
                        // Insert header row and place cursor in first header
                        const text = "||~Header 1||~Header 2||";
                        view.dispatch({
                            changes: { from, to, insert: text },
                            selection: { anchor: from + 3 } // cursor after ||~
                        });
                    }, 
                    detail: "header row" 
                },
                { 
                    label: "|| Cell 1 || Cell 2 ||", 
                    type: "keyword", 
                    apply: (view, completion, from, to) => {
                        // Insert table row and place cursor in first cell
                        const text = "||Cell 1||Cell 2||";
                        view.dispatch({
                            changes: { from, to, insert: text },
                            selection: { anchor: from + 2 } // cursor after ||
                        });
                    }, 
                    detail: "table row" 
                }
            ],
            filter: true
        };
    }

    // If cursor is inside class="", provide common CSS class completions
    if (classMatch && (classMatch.from !== classMatch.to || context.explicit)) {
    // Provide class value completions
    return {
        from: classMatch.from,
        options: [
             // Theme/layout div autocomplete
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
                detail: "container" 
            },
            {
                label: "blockquote",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert blockquote class name
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

    // Do not trigger if no "[[" match is found
    if (!before || before.from == before.to && !context.explicit) return {
        from: context.pos,
        options: []
    };

    return {
        from: before.from,
        options: [
            // Common tags
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
                detail: "container" 
            },
            {
                label: "[[size ",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    const text = "[[size ]]\n\n[[/size";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[size ".length } // cursor after size
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
                        selection: { anchor: from + text.length } // cursor after tag name
                    });
                }, 
                detail: "include page" 
            },
            {
                label: "[[tabview",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert tabview tag, cursor after tag name
                    const text = "[[tabview]]\n[[/tabview";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[tabview".length } // cursor after tag name
                    });
                },
                detail: "tab view"
            },
            {
                label: "[[tab", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert tab tag, cursor after tab
                    const text = "[[tab ]]\n[[/tab";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[tab ".length } // cursor after tab
                    });
                }, 
                detail: "tab" 
            },
            {
                label: "[[include :scp-wiki",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert branch wiki include tag, cursor after insertion
                    const text = "[[include :scp-wiki";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // cursor after tag name
                    });
                },
                detail: "SCP-Wiki"
            },
            {
                label: "[[include :scp-wiki-cn",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert theme include tag, cursor after insertion
                    const text = "[[include :scp-wiki-cn:theme:";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // cursor after tag name
                    });
                },
                detail: "theme"
            },
            {
                label: "[[include :scp-wiki-cn:component:",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert component include tag, cursor after insertion
                    const text = "[[include :scp-wiki-cn:component:";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // cursor after tag name
                    });
                },
                detail: "component"
            },
            {
                label: "[[include :scp-wiki-cn:component:acs-animation",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert acs-animation include tag
                    const text = "[[include :scp-wiki-cn:component:acs-animation";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "acs-animation"
            },
            {
                label: "[[include :scp-wiki-cn:component:wxchat-backend",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    const text = "[[include :scp-wiki-cn:component:wxchat-backend inc-top=--]\n|title=Best Friends Group\n|opacity=1\n|groupmode=true\n|theme=dark\n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "wxchat-backend"
            },
            {
                label: "[[include :scp-wiki-cn:component:wxchat-backend inc-right=--]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    const text = "[[include :scp-wiki-cn:component:wxchat-backend inc-right=--]\n|name=username1\n|pure-message=true\n|icon=http://urlhere.com\n|color=white\n|content=content1\n|voice=true\n|voice-time=60\n|voice-content=content1\n|content=content1\n|image=true\n|image-url=http://urlhere.com\n|reply=true\n|reply-name=username2\n|reply-content=content2\n|blacklist=true\n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "wxchat-backend inc-right"
            },
            {
                label: "[[include :scp-wiki-cn:component:wxchat-backend inc-left=--]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    const text = "[[include :scp-wiki-cn:component:wxchat-backend inc-left=--]\n|name=username1\n|pure-message=true\n|icon=http://urlhere.com\n|color=white\n|content=content1\n|voice=true\n|voice-time=60\n|voice-content=content1\n|content=content1\n|image=true\n|image-url=http://urlhere.com\n|reply=true\n|reply-name=username2\n|reply-content=content2\n|blacklist=true\n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "wxchat-backend inc-left"
            },
            {
                label: "[[include :scp-wiki-cn:component:wxchat-backend inc-tip=--]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    const text = "[[include :scp-wiki-cn:component:wxchat-backend inc-tip=--]\n|content=Message sent, but refused by recipient.\n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "wxchat-backend inc-tip"
            },
            {
                label: "[[include :scp-wiki-cn:component:wxchat-backend inc-end=--]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    const text = "[[include :scp-wiki-cn:component:wxchat-backend inc-end=--]\n|content=none\n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "wxchat-backend inc-end"
            },
            {
                label: "[[include :scp-wiki-cn:component:anomaly-class-bar-source",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert anomaly-class-bar-source include tag
                    const text = "[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number=SCP-CN-XXXX\n|clearance= \n|container-class= \n|disruption= \n|risk-class= \n";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + 80, head: from + 91 } // cursor after tag name
                    });
                },
                detail: "ACS",
                source: "10000000000000000000000000000000000000000000000000000000000000000000000000000000000000" // set a high priority
            },
            {
                label: "[[include :scp-wiki-cn:component:advanced-information-methodaology",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert advanced-information-methodaology include tag
                    const text = "[[include :scp-wiki-cn:component:advanced-information-methodaology\n|lang=cn\n|XXXX=SCP-XXXX\n|lv=Level\n|cc= \n|dc= \n|site= \n|dir= \n|head= \n|mtf= \n";
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
                    // Insert license-box include tag
                    const text = "[[include :scp-wiki-cn:component:license-box\n|lang=cn\n|author= \n]]\n=====\n> File name:\n> Image name: \n> Image author: \n> License: \n> Source link:\n=====\n[[include :scp-wiki-cn:component:license-end";
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
                    // Insert span tag, cursor at attribute position
                    const text = "[[span class=\"\"]]\n\n[[/span";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[span class=\"".length } // cursor between class quotes
                    });
                }
            },
            {
                label: "[[collapsible]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert collapsible tag, cursor after tag name
                    const text = "[[collapsible show=\"+\" hide=\"-\"]]\n[[/collapsible";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[collapsible".length + 8 } // cursor after tag name
                    });
                },
                detail: "collapsible content"
            },
            {
                label: "[[note",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert note
                    const text = "[[note]]\n\n[[/note";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[note]]\n".length }
                    });
                },
                detail: "note"
            },
            {
                label: "[[user",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert user
                    const text = "[[*user "
                    view.dispatch({
                        changes: { from, to, insert: text},
                        selection: { anchor: from + "[[#user ".length }
                    });
                },
                detail: "user avatar"
            },
            { 
                label: "[[module ", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert module tag, cursor at module name
                    const text = "[[module ";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // cursor after tag name
                    });
                }, 
                detail: "functional module" 
            },
            {
                label: "[[module css]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert css module, cursor inside tag
                    const text = "[[module css]]\n\n[[/module";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[module css".length + 2 } // cursor inside tag
                    });
                },
                detail: "CSS module"
            },
            {
                label: "[[html]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert html module, cursor inside tag
                    const text = "[[html]]\n\n[[/html";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[html".length + 2 } // cursor inside tag
                    });
                },
                detail: "HTML module"

            },

            // More Wikidot tags can be added here
            { 
                label: "[[module rate]]", 
                type: "function", 
                apply: (view, completion, from, to) => {
                    // Insert rate module, cursor inside tag
                    const text = "[[module rate";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length + 2 }
                    });
                }, 
                detail: "rating module" 
            },
            { 
                label: "[[code]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert code block, cursor between type="" quotes
                    const text = "[[code type=\"\"]]\n\n[[/code";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + "[[code type=\"".length } // cursor inside quotes
                    });
                }, 
                detail: "code block" 
            },
            { 
                label: "[[>]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert right-align tag and select content area
                    const text = "[[>]]\nAligned content\n[[/>";
                    const selectFrom = from + "[[>]]\n".length;
                    const selectTo = selectFrom + "Aligned content".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "right align" 
            },
            { 
                label: "[[<]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert left-align tag and select content area
                    const text = "[[<]]\nAligned content\n[[/<";
                    const selectFrom = from + "[[<]]\n".length;
                    const selectTo = selectFrom + "Aligned content".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "left align" 
            },
            { 
                label: "[[=]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert center-align tag and select content area
                    const text = "[[=]]\nCentered content\n[[/=";
                    const selectFrom = from + "[[=]]\n".length;
                    const selectTo = selectFrom + "Centered content".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "center align" 
            },
            { 
                label: "[[image ", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert image tag, cursor at attribute position
                    const text = "[[image ";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length } // cursor after tag name
                    });
                }, 
                detail: "image" 
            },
            {
                label: "[[include component:image-block",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert image-block include snippet
                    const text = "[[include component:image-block\n|name= \n|caption= \n|width= \n|height= \n|align= ";
                    const selectFrom = from + "[[include component:image-block\n|name=".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom } // cursor
                    });
                }, 
                detail: "image block"
            },
            { 
                label: "[[footnote]]", 
                type: "keyword", 
                apply: (view, completion, from, to) => {
                    // Insert footnote tag and select footnote text
                    const text = "[[footnote]]This is a footnote[[/footnote";
                    const selectFrom = from + "[[footnote]]".length;
                    const selectTo = selectFrom + "This is a footnote".length;
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: selectFrom, head: selectTo }
                    });
                }, 
                detail: "footnote" 
            },
            {
                label: "[[footnoteblock]]",
                type: "keyword",
                apply: (view, completion, from, to) => {
                    // Insert footnote block tag
                    const text = "[[footnoteblock";
                    view.dispatch({
                        changes: { from, to, insert: text },
                        selection: { anchor: from + text.length }
                    });
                },
                detail: "footnote block"
            },
        ],
        filter: true 
    };
};
