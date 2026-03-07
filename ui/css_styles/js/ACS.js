//  ACS 异常分类系统
const COLOR_MAP = {
    'safe': '#27ae60',
    'euclid': '#f1c40f',
    'keter': '#c0392b',
    'neutralized': '#7f8c8d', // Gray
    'pending': '#bdc3c7',     // Light Gray
    'explained': '#95a5a6',   // Gray
    'esoteric': '#595959'     // Dark Gray
};

const ACS_ICON_MAP = {
    'apollyon': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/apollyon-icon.svg',
    'archon': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/archon-icon.svg',
    'hiemal': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/hiemal-icon.svg',
    'tiamat': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/tiamat-icon.svg',
    'ticonderoga': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/ticonderoga-icon.svg',
    'thaumiel': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/thaumiel-icon.svg'
};

function applyAcsChange(element, className) {
    const acsBox = element.closest('.acs-box');
    if (!acsBox) return;
    const val = className.toLowerCase();
    if (COLOR_MAP[val]) {
        acsBox.style.setProperty('--acs-color', COLOR_MAP[val]);
        acsBox.setAttribute('data-container', val);
        const label = acsBox.querySelector('[data-field="container"]');
        if (label) label.innerText = className;

        // Auto-cleanup Secondary if not Esoteric
        if (val !== 'esoteric') {
            const secLabel = acsBox.querySelector('[data-field="secondary"]');
            const iconLabel = acsBox.querySelector('[data-field="secondary-icon"]');
            if (secLabel && secLabel.innerText.toLowerCase() !== 'none') {
                secLabel.innerText = 'none';
                if (iconLabel) iconLabel.innerText = '';
                // Update internal state/styles if needed, though secondary styling is minimal
            }
        }
    }
}

function applyAcsSecondary(element, className) {
    const acsBox = element.closest('.acs-box');
    if (!acsBox) return;
    const label = acsBox.querySelector('[data-field="secondary"]');
    if (label) label.innerText = className;

    const val = className.toLowerCase();

    // Auto-fill Icon
    const iconLabel = acsBox.querySelector('[data-field="secondary-icon"]');
    if (iconLabel) {
        if (ACS_ICON_MAP[val]) {
            iconLabel.innerText = ACS_ICON_MAP[val];
        } else if (val === 'none') {
            iconLabel.innerText = '';
        }
    }

    // Auto switch to esoteric if secondary is present
    if (className.toLowerCase() !== 'none') {
        const containerLabel = acsBox.querySelector('[data-field="container"]');
        if (containerLabel) {
            containerLabel.innerText = 'Esoteric';
            applyAcsChange(containerLabel, 'Esoteric');
        }
    }
}