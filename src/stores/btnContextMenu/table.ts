import {
    addColumn,
    addRow,
    isInTable,
    selectedRect,
    TableMap,
} from "@tiptap/pm/tables";
import type { Node as ProseMirrorNode } from "@tiptap/pm/model";
import type { Transaction } from "@tiptap/pm/state";
import { getEditor } from "../editor.ts";

// Placeholder seeded into freshly created cells, matching table insertion.
// Empty cells render as blank Wikidot cells (`|| ||`) and are awkward to click
// into, so new rows/columns ship with visible "TABLE" content to overwrite.
const TABLE_CELL_PLACEHOLDER = "TABLE";

/**
 * Replace the inner content of the given cells with a single `"TABLE"`
 * paragraph. Ranges are applied back-to-front so earlier positions stay valid
 * as the document grows.
 */
function fillCellContents(
    tr: Transaction,
    table: ProseMirrorNode,
    cellRanges: { from: number; to: number }[],
) {
    const placeholder = table.type.schema.nodes.paragraph.create(
        null,
        table.type.schema.text(TABLE_CELL_PLACEHOLDER),
    );

    cellRanges
        .sort((a, b) => b.from - a.from)
        .forEach(({ from, to }) => tr.replaceWith(from, to, placeholder));
}

function cellContentRange(cellStart: number, cell: ProseMirrorNode) {
    const from = cellStart + 1;
    return { from, to: from + cell.content.size };
}

export function addTableColumn() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    editor
        .chain()
        .focus()
        .command(({ state, tr, dispatch }) => {
            if (!isInTable(state)) {
                return false;
            }

            if (!dispatch) {
                return true;
            }

            const rect = selectedRect(state);
            const col = rect.right;

            addColumn(tr, rect, col);

            const table = tr.doc.nodeAt(rect.tableStart - 1);
            if (!table) {
                return true;
            }

            // A cell that *starts* at the inserted column is necessarily new;
            // colspan-extended cells start earlier and are left untouched.
            const map = TableMap.get(table);
            const seen = new Set<number>();
            const ranges: { from: number; to: number }[] = [];

            for (let row = 0; row < map.height; row += 1) {
                const offset = map.map[row * map.width + col];

                if (map.colCount(offset) !== col || seen.has(offset)) {
                    continue;
                }

                seen.add(offset);

                const cellStart = rect.tableStart + offset;
                const cell = tr.doc.nodeAt(cellStart);

                if (cell) {
                    ranges.push(cellContentRange(cellStart, cell));
                }
            }

            fillCellContents(tr, table, ranges);

            return true;
        })
        .run();
}

export function addTableRow() {
    const editor = getEditor();

    if (!editor) {
        return;
    }

    editor
        .chain()
        .focus()
        .command(({ state, tr, dispatch }) => {
            if (!isInTable(state)) {
                return false;
            }

            if (!dispatch) {
                return true;
            }

            const rect = selectedRect(state);
            const rowIndex = rect.bottom;

            addRow(tr, rect, rowIndex);

            const table = tr.doc.nodeAt(rect.tableStart - 1);
            if (!table) {
                return true;
            }

            // The freshly inserted row sits at child index `rowIndex` and holds
            // only its own new cells (rowspan-extended cells stay in earlier
            // rows), so every cell in it is safe to seed.
            let rowStart = rect.tableStart;
            for (let i = 0; i < rowIndex; i += 1) {
                rowStart += table.child(i).nodeSize;
            }

            const newRow = table.child(rowIndex);
            const ranges: { from: number; to: number }[] = [];

            newRow.forEach((cell, cellOffset) => {
                ranges.push(cellContentRange(rowStart + 1 + cellOffset, cell));
            });

            fillCellContents(tr, table, ranges);

            return true;
        })
        .run();
}

export function deleteTableColumn() {
    getEditor()?.chain().focus().deleteColumn().run();
}

export function deleteTableRow() {
    getEditor()?.chain().focus().deleteRow().run();
}

export function deleteTable() {
    getEditor()?.chain().focus().deleteTable().run();
}
