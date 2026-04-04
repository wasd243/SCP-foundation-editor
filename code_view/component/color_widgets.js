// color_widgets.js - 修复版
import { EditorView, Decoration } from "@codemirror/view";
import { RangeSetBuilder } from "@codemirror/state";

// Wikidot颜色标签装饰器扩展
export const wikidotColorExtension = EditorView.decorations.of((view) => {
    const builder = new RangeSetBuilder();
    const text = view.state.doc.toString();
    
    // 匹配Wikidot颜色标签：###ffffff|文字##
    // 注意：结束标记是 ##，不是 ###
    const wikidotColorRegex = /###([0-9a-fA-F]{6})\|([^#]*)##/g;
    let match;
    
    while ((match = wikidotColorRegex.exec(text)) !== null) {
        try {
            const fullMatch = match[0];
            const colorCode = "#" + match[1];
            const content = match[2];
            const start = match.index;
            const end = start + fullMatch.length;
            
            // 计算文字内容的开始位置（跳过 ###ffffff|）
            // "###ffffff|" 总共10个字符：3个# + 6个十六进制字符 + 1个|
            const colorPartLength = 10;
            const contentStart = start + colorPartLength;
            const contentEnd = contentStart + content.length;
            
            // 为文字内容部分添加颜色样式
            if (content.length > 0) {
                builder.add(
                    contentStart,
                    contentEnd,
                    Decoration.mark({
                        attributes: {
                            style: `color: ${colorCode}; font-weight: normal!important;`,
                            class: "cm-wikidot-colored-text"
                        }
                    })
                );
            }
            
            console.log(`匹配到Wikidot颜色标签: ${fullMatch}`);
            console.log(`颜色代码: ${colorCode}, 内容: "${content}"`);
            console.log(`位置: ${start}-${end}, 内容位置: ${contentStart}-${contentEnd}`);
        } catch (error) {
            console.error("处理Wikidot颜色标签时出错:", error, match);
        }
    }
    
    return builder.finish();
});
