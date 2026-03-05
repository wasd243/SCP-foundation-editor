function refreshFootnotes() {
    if (document.activeElement && document.activeElement.closest('#footnote-list-footer')) return;
    const editor = document.getElementById('editor-root');
    const footer = document.getElementById('footnote-list-footer');
    const footnotes = editor.querySelectorAll('.scp-footnote');
    if (footnotes.length === 0) { footer.innerHTML = ""; return; }
    let html = "<b>脚注预览 (可编辑):</b><br>";
    footnotes.forEach((fn, index) => {
        const num = index + 1;
        if (fn.innerText != num) fn.innerText = num;
        const content = fn.getAttribute('data-content') || '待输入';
        html += `<div class="footnote-list-item"><span style="color:#B22222;font-weight:bold;">${num}.</span> <span class="footnote-content" contenteditable="true" oninput="updateFootnoteFromPreview(${index}, this)">${content}</span></div>`;
    });
    if (footer.innerHTML !== html) footer.innerHTML = html;
}

function updateFootnoteFromPreview(index, el) {
    const editor = document.getElementById('editor-root');
    const footnotes = editor.querySelectorAll('.scp-footnote');
    if (footnotes[index]) {
        const txt = el.innerText;
        footnotes[index].setAttribute('data-content', txt);
        footnotes[index].setAttribute('title', txt);
    }
}