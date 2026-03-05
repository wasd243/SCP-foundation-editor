function toggleCss(header) {
    // Find the css content div
    var parent = header.parentElement;
    var content = parent.querySelector('.css-content');
    if (content) {
        if (content.style.display === 'none') {
            content.style.display = 'block';
            header.innerText = header.innerText.replace(' (点击展开)', ' (点击折叠)');
        } else {
            content.style.display = 'none';
            header.innerText = header.innerText.replace(' (点击折叠)', ' (点击展开)');
            if (!header.innerText.includes(' (点击展开)')) header.innerText += ' (点击展开)';
        }
    }
}
