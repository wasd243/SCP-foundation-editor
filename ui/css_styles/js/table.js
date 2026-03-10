function tableAction(action) {
    const sel = window.getSelection();
    if (!sel.rangeCount) return;
    const cell = sel.anchorNode.nodeType === 3 ? sel.anchorNode.parentElement.closest('td, th') : sel.anchorNode.closest('td, th');
    if (!cell) return;
    const row = cell.parentElement;
    const table = row.parentElement.closest('table');
    const rows = Array.from(table.rows);
    const rowIndex = row.rowIndex;
    const colIndex = cell.cellIndex;

    if (action === 'addRow') {
        const newRow = table.insertRow(rowIndex + 1);
        for (let i = 0; i < row.cells.length; i++) {
            const newCell = newRow.insertCell(i);
            newCell.innerText = '内容';
            newCell.setAttribute('contenteditable', 'true');
        }
    } else if (action === 'delRow') {
        table.deleteRow(rowIndex);
        if (table.rows.length === 0) table.remove();
    } else if (action === 'addCol') {
        for (let i = 0; i < rows.length; i++) {
            let isHeader = false;
            // Check if current cell at the same column index in this row is TH
            if (rows[i].cells[colIndex] && rows[i].cells[colIndex].tagName === 'TH') {
                isHeader = true;
            }

            // Generate the new cell right after the current column index
            const newCell = document.createElement(isHeader ? 'th' : 'td');
            newCell.innerText = '内容';
            newCell.setAttribute('contenteditable', 'true');

            // Insert it
            const refCell = rows[i].cells[colIndex];
            if (refCell) {
                refCell.insertAdjacentElement('afterend', newCell);
            } else {
                rows[i].appendChild(newCell);
            }
        }
    } else if (action === 'delCol') {
        for (let i = 0; i < rows.length; i++) {
            if (rows[i].cells.length > colIndex) {
                rows[i].deleteCell(colIndex);
            }
        }
        if (table.rows[0] && table.rows[0].cells.length === 0) table.remove();
    } else if (action === 'delTable') {
        table.remove();
    } else if (action === 'mergeRight') {
        if (colIndex < row.cells.length - 1) {
            const nextCell = row.cells[colIndex + 1];
            const currentColSpan = parseInt(cell.getAttribute('colspan') || 1);
            const nextColSpan = parseInt(nextCell.getAttribute('colspan') || 1);
            cell.setAttribute('colspan', currentColSpan + nextColSpan);
            if (nextCell.innerText.trim()) cell.innerHTML += ' ' + nextCell.innerHTML;
            row.deleteCell(colIndex + 1);
        }
    } else if (action === 'toggleBorder') {
        if (table.classList.contains('no-border')) {
            table.classList.remove('no-border');
            table.setAttribute('border', '1');
        } else {
            table.classList.add('no-border');
            table.setAttribute('border', '0');
        }
    }
}

function insertTable() {
    const html = `
                    <table border="1" class="wikidot-table">
                        <tr><th contenteditable="true">~ 标题 1</th><th contenteditable="true">~ 标题 2</th><th contenteditable="true">~ 标题 3</th></tr>
                        <tr><td contenteditable="true">内容 1</td><td contenteditable="true">内容 2</td><td contenteditable="true">内容 3</td></tr>
                        <tr><td contenteditable="true">内容 4</td><td contenteditable="true">内容 5</td><td contenteditable="true">内容 6</td></tr>
                    </table><p><br></p>`;
    document.execCommand('insertHTML', false, html);
}