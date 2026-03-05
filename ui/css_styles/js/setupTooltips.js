let tooltip = null;
let fnTooltip = null;
// 悬停提示

function setupTooltips() {
    tooltip = document.createElement('div');
    tooltip.id = 'component-tooltip';
    document.body.appendChild(tooltip);

    fnTooltip = document.createElement('div');
    fnTooltip.id = 'footnote-preview-tooltip';
    document.body.appendChild(fnTooltip);

    document.addEventListener('mouseover', (e) => {
        // Component Tooltip
        const comp = e.target.closest('.scp-component, .wikidot-table');
        const isFooter = e.target.closest('#footnote-list-footer');

        if (comp && !isFooter) {
            let type = comp.getAttribute('data-type') || 'Unknown Component';
            if (comp.classList.contains('wikidot-table')) type = "Table";
            if (comp.classList.contains('rate-module-box')) type = "Rate Module";
            // Specific names
            if (type === 'acs') type = "ACS Component";
            if (type === 'image-block') type = "Image Block";
            if (type === 'image-block-adv') type = "Adv Image";
            if (type === 'tabview') type = "Tab View";
            if (type === 'collapsible') type = "Collapsible";
            if (type === 'email-example') type = "电子邮件模版";

            if (type !== 'footnote') {
                tooltip.innerText = type;
                tooltip.style.display = 'block';

                // Position logic
                const rect = comp.getBoundingClientRect();
                tooltip.style.left = rect.left + 'px';
                tooltip.style.top = (rect.top - 25) + 'px';
            } else {
                tooltip.style.display = 'none';
            }
        } else {

            tooltip.style.display = 'none';
        }

        // Footnote Hover
        const fn = e.target.closest('.scp-footnote');
        if (fn) {
            const content = fn.getAttribute('data-content') || '无内容';
            fnTooltip.innerText = content;
            fnTooltip.style.display = 'block';

            const rect = fn.getBoundingClientRect();
            fnTooltip.style.left = (rect.left + 20) + 'px';
            fnTooltip.style.top = (rect.top + 20) + 'px';
        } else {
            fnTooltip.style.display = 'none';
        }
    });

    document.addEventListener('mouseout', (e) => {
        // Simple hide on mouseout of window/body? 
        // Check relatedTarget
        if (!e.relatedTarget) {
            tooltip.style.display = 'none';
            fnTooltip.style.display = 'none';
        }
    });

    document.addEventListener('click', (e) => {
        const fn = e.target.closest('.scp-footnote');
        if (fn) {
            // Find index
            const allFn = Array.from(document.querySelectorAll('.scp-footnote'));
            const index = allFn.indexOf(fn);
            if (index !== -1) {
                window.location.href = "edit-footnote://" + index;
            }
        }
    });
}
