// --- Helper Functions for Collapsible Modules ---
function toggleDiv(header) {
    var content = header.nextElementSibling;
    if (content) {
        if (content.style.display === 'none') {
            content.style.display = 'block';
            header.classList.remove('collapsed');
        } else {
            content.style.display = 'none';
            header.classList.add('collapsed');
        }
    }
}