function handleTitleMarkdown() {
    // 处理标题的 Markdown 语法
    const sel = window.getSelection();
    if (!sel.rangeCount) return;
    const range = sel.getRangeAt(0);
    let node = range.startContainer;
    let block = node;
    while (block && block.parentNode && block.parentNode.id !== 'editor-root') block = block.parentNode;
    if (block && block.nodeType === 1 && block.id !== 'editor-root') {
        const text = block.innerText;
        // Avoid unnecessary regex matches on empty lines or non-title lines
        if (!text || !text.startsWith('+')) return;

        // 匹配 1-6 个 + 号后面跟空格
        const match = text.match(/^([+]{1,6})\s+(.*)/);
        if (match) {
            const level = match[1].length;
            const content = match[2];
            const hTag = 'H' + level;
            
            if (block.tagName !== hTag) {
                const newH = document.createElement(hTag);
                newH.innerText = content;
                block.parentNode.replaceChild(newH, block);
                
                // 将光标定位到末尾
                const newRange = document.createRange();
                newRange.selectNodeContents(newH);
                newRange.collapse(false);
                sel.removeAllRanges();
                sel.addRange(newRange);
            }
        }
    }
}

// 绑定事件到编辑器根节点
document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('editor-root');
    if (!root) return;

    // 监控输入，实时转换标题
    root.addEventListener('input', (e) => {
        handleTitleMarkdown();
    });

    // 处理回车键逻辑：标题回车自动转为正文
    root.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const sel = window.getSelection();
            if (!sel.rangeCount) return;
            const range = sel.getRangeAt(0);
            let node = range.startContainer;
            if (node.nodeType === 3) node = node.parentNode;
            
            const heading = node.closest('h1, h2, h3, h4, h5, h6');
            if (heading) {
                // 检查是否在行末执行回车
                // 如果是，则手动插入一个 <p> 标签并跳转
                if (range.collapsed && range.endOffset === node.textContent.length) {
                    e.preventDefault();
                    const p = document.createElement('p');
                    p.innerHTML = '<br>';
                    heading.after(p);
                    
                    const newRange = document.createRange();
                    newRange.setStart(p, 0);
                    newRange.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(newRange);
                }
            }
        }
    });
});