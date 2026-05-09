// color_widgets.js - fixed version
import { EditorView, Decoration } from "@codemirror/view";
import { RangeSetBuilder } from "@codemirror/state";

// Wikidot color-tag decorator extension
export const wikidotColorExtension = EditorView.decorations.of((view) => {
    const builder = new RangeSetBuilder();
    const text = view.state.doc.toString();
    
    // Match Wikidot color tags: ###ffffff|text##
    // Note: the closing marker is ##, not ###
    const wikidotColorRegex = /###([0-9a-fA-F]{6})\|([^#]*)##/g;
    let match;
    
    while ((match = wikidotColorRegex.exec(text)) !== null) {
        try {
            const fullMatch = match[0];
            const colorCode = "#" + match[1];
            const content = match[2];
            const start = match.index;
            const end = start + fullMatch.length;
            
            // Calculate content start position (skip ###ffffff|)
            // "###ffffff|" has 10 chars: 3 # + 6 hex chars + 1 |
            const colorPartLength = 10;
            const contentStart = start + colorPartLength;
            const contentEnd = contentStart + content.length;
            
            // Apply color style to the text content segment
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
            
            console.log(`Matched Wikidot color tag: ${fullMatch}`);
            console.log(`Color code: ${colorCode}, content: "${content}"`);
            console.log(`Range: ${start}-${end}, content range: ${contentStart}-${contentEnd}`);
        } catch (error) {
            console.error("Error while processing Wikidot color tag:", error, match);
        }
    }
    
    return builder.finish();
});
