(function () {
    var editor = document.getElementById('editor-root');
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
    var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;

    var divBox = document.createElement('div');
    divBox.className = 'scp-component foundation-bg-box';
    divBox.setAttribute('data-type', 'foundation-bg');
    divBox.setAttribute('contenteditable', 'false');

    divBox.style.position = 'relative';
    divBox.style.width = 'auto';
    divBox.style.textAlign = 'center';
    divBox.style.clear = 'both';
    divBox.style.minHeight = '300px';
    divBox.style.margin = '20px 0';

    var bgBlock = document.createElement('div');
    bgBlock.style.position = 'absolute';
    bgBlock.style.top = '0';
    bgBlock.style.bottom = '0';
    bgBlock.style.left = '0';
    bgBlock.style.right = '0';
    bgBlock.style.width = '295px';
    bgBlock.style.height = '295px';
    bgBlock.style.margin = 'auto';
    bgBlock.style.backgroundImage = 'url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png)';
    bgBlock.style.backgroundSize = '295px 295px';
    bgBlock.style.backgroundRepeat = 'no-repeat';
    bgBlock.style.backgroundPosition = 'center';
    bgBlock.style.zIndex = '0';
    bgBlock.style.opacity = '0.3';
    divBox.appendChild(bgBlock);

    var textContainer = document.createElement('div');
    textContainer.style.position = 'relative';
    textContainer.style.zIndex = '1';
    textContainer.style.width = '100%';
    textContainer.style.height = '295px';

    var titleDiv = document.createElement('div');
    titleDiv.className = 'foundation-title';
    titleDiv.style.position = 'absolute';
    titleDiv.style.left = '0';
    titleDiv.style.right = '0';
    titleDiv.style.top = '38px';
    titleDiv.setAttribute('contenteditable', 'true');
    var h1Title = document.createElement('h1');
    h1Title.style.fontSize = '220%';
    h1Title.style.color = '#555';
    h1Title.style.margin = '0';
    h1Title.innerHTML = '标题';
    titleDiv.appendChild(h1Title);
    textContainer.appendChild(titleDiv);

    var descDiv = document.createElement('div');
    descDiv.className = 'foundation-desc';
    descDiv.style.position = 'absolute';
    descDiv.style.left = '0';
    descDiv.style.right = '0';
    descDiv.style.top = '85px';
    descDiv.style.width = '100%';
    descDiv.setAttribute('contenteditable', 'true');

    var descH1 = document.createElement('h1');
    descH1.style.fontSize = '120%';
    descH1.style.color = '#555';
    descH1.style.margin = '0';
    descH1.innerHTML = '副标题';
    descDiv.appendChild(descH1);

    var descP = document.createElement('p');
    descP.style.fontSize = '90%';
    descP.style.color = '#555';
    descP.style.margin = '0';
    descP.innerHTML = '描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述';
    descDiv.appendChild(descP);
    textContainer.appendChild(descDiv);

    var itemDiv = document.createElement('div');
    itemDiv.className = 'foundation-itemno';
    itemDiv.style.position = 'absolute';
    itemDiv.style.left = '0';
    itemDiv.style.right = '0';
    itemDiv.style.bottom = '27px';
    itemDiv.setAttribute('contenteditable', 'true');
    var h1Item = document.createElement('h1');
    h1Item.style.fontSize = '170%';
    h1Item.style.color = '#555';
    h1Item.style.margin = '0';
    h1Item.innerHTML = 'XXXX';
    itemDiv.appendChild(h1Item);
    textContainer.appendChild(itemDiv);

    divBox.appendChild(textContainer);

    var cssIndicator = document.createElement('div');
    cssIndicator.className = 'foundation-css-indicator';
    cssIndicator.setAttribute('contenteditable', 'false');
    cssIndicator.style.backgroundColor = '#f0f0f0';
    cssIndicator.style.border = '1px solid #ccc';
    cssIndicator.style.padding = '5px';
    cssIndicator.style.marginTop = '10px';
    cssIndicator.style.fontSize = '12px';
    cssIndicator.style.color = '#666';
    cssIndicator.style.fontFamily = 'monospace';
    cssIndicator.style.textAlign = 'left';
    cssIndicator.innerHTML = '<i>[CSS模块已折叠连体，导出时将自动附带相应的格式代码]</i>';
    divBox.appendChild(cssIndicator);

    if (comp) {
        if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {
            comp.parentNode.replaceChild(divBox, comp);
        } else {
            comp.parentNode.insertBefore(divBox, comp.nextSibling);
        }
    } else {
        editor.appendChild(divBox);
    }

    var endP = document.createElement('p');
    endP.innerHTML = '<br>';
    if (divBox.nextSibling) {
        divBox.parentNode.insertBefore(endP, divBox.nextSibling);
    } else {
        divBox.parentNode.appendChild(endP);
    }
})();