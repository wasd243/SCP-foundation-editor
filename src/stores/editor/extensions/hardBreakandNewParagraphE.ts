import { Extension } from "@tiptap/core";
import type { ResolvedPos } from "@tiptap/pm/model";

import { nodeHasClass } from "./WJtags/htmlPreserveE.ts";

// Single Enter inserts a `hardBreak` (exported as a Wikidot `NewLine`); a second
// Enter promotes the provisional break into a real paragraph split. This inverts
// ProseMirror's default Enter behavior to match Wikidot line-break semantics.

const EXCLUDED_ANCESTOR_TYPES = ["listItem", "tableCell", "tableHeader"];
const IMAGE_CAPTION_CLASS = "scp-image-caption";

// Returns true when the cursor sits inside a context that owns its own Enter
// behavior (lists, table cells, image captions), so we leave it untouched.
function hasExcludedAncestor($from: ResolvedPos) {
    for (let depth = $from.depth; depth > 0; depth -= 1) {
        const node = $from.node(depth);

        if (EXCLUDED_ANCESTOR_TYPES.includes(node.type.name)) {
            return true;
        }

        if (nodeHasClass(node, IMAGE_CAPTION_CLASS)) {
            return true;
        }
    }

    return false;
}

export const HardBreakAndNewParagraphExtension = Extension.create({
    name: "hardBreakAndNewParagraph",

    addKeyboardShortcuts() {
        return {
            Enter: () => {
                const { selection } = this.editor.state;

                // Only handle a plain collapsed caret; selections fall through to
                // the default replace-and-split behavior.
                if (!selection.empty) {
                    return false;
                }

                const { $from } = selection;

                // Only act inside ordinary paragraphs; everything else (headings,
                // code blocks, details summary, tabview buttons, lists, table
                // cells, captions) keeps its existing Enter handling.
                if ($from.parent.type.name !== "paragraph") {
                    return false;
                }

                if (hasExcludedAncestor($from)) {
                    return false;
                }

                const nodeBefore = $from.nodeBefore;

                if (nodeBefore?.type.name === "hardBreak") {
                    // Double Enter: drop the provisional hardBreak, then split so
                    // the exporter sees a clean paragraph boundary (no stray
                    // trailing NewLine / blank line).
                    return this.editor
                        .chain()
                        .deleteRange({
                            from: $from.pos - nodeBefore.nodeSize,
                            to: $from.pos,
                        })
                        .splitBlock()
                        .run();
                }

                // Single Enter: insert a hardBreak (Wikidot newline).
                return this.editor.commands.setHardBreak();
            },
        };
    },
});
