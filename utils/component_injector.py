import json

def inject_terminal_shortcut(page, x, y):
    term_css = """
.danke{
padding: 5px 5px 5px 15px;
margin-bottom:10px;
font-family: 'Courier New', monospace;
font-size: 1.1em; }

.agent{
background-color:#000000;
border: 3px solid #55AA55;
color: #77CC77;
}

.site{
background-color:#222200;
border: 3px solid #AAAA55;
color: #DDDD77;
}
"""
    term_div_content = """<div class="div-header" contenteditable="true">DIV: class="danke agent"</div><div class="div-content" contenteditable="true">| 细节<br>| 细节<br>| 细节<br>| 细节<br>| 细节<br><br>文字 文字 文字<br>更多文字<br><br>更多<br><br>以及更多<br><br>甚至还有更多要记录的文字</div>"""
    
    safe_css = term_css.replace('\n', '\\n').replace('"', '\\"')
    safe_div = term_div_content.replace('\n', '\\n').replace('"', '\\"')

    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component') : null;
        var type = comp ? comp.getAttribute('data-type') : null;

        var cssContent = "{safe_css}";
        var divHtml = '{safe_div}';
        
        function createCssEl() {{
            var box = document.createElement('div');
            box.className = 'scp-component css-box';
            box.setAttribute('data-type', 'css-module');
            box.setAttribute('contenteditable', 'false');
            box.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
            return box;
        }}
        
        function createDivEl() {{
            var divBox = document.createElement('div');
            divBox.className = 'scp-component div-box';
            divBox.setAttribute('data-type', 'div-block');
            divBox.setAttribute('contenteditable', 'false');
            divBox.innerHTML = '{safe_div}';
            return divBox;
        }}
        
        function hasTerminalCss() {{
             var css = document.querySelectorAll('.css-box .css-content');
             for(var i=0; i<css.length; i++) {{
                 if(css[i].innerText.indexOf('.danke') !== -1 && css[i].innerText.indexOf('.agent') !== -1) return true;
             }}
             return false;
        }}

        if (type === 'css-module') {{
            comp.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
            var next = comp.nextElementSibling;
            var needDiv = true;
            if (next && next.classList.contains('div-box')) {{
                var header = next.querySelector('.div-header');
                if (header && (header.innerText.indexOf('danke') !== -1 || header.innerText.indexOf('agent') !== -1)) {{
                    needDiv = false;
                }}
            }}
            if (needDiv) {{ comp.parentNode.insertBefore(createDivEl(), comp.nextSibling); }}
        }} else if (type === 'div-block') {{
            var newDiv = createDivEl();
            comp.parentNode.replaceChild(newDiv, comp);
            if (!hasTerminalCss()) {{ editor.insertBefore(createCssEl(), editor.firstChild); }}
        }} else {{
            if (!hasTerminalCss()) {{ editor.insertBefore(createCssEl(), editor.firstChild); }}
            if (comp) {{ comp.parentNode.insertBefore(createDivEl(), comp.nextSibling); }} 
            else {{ editor.appendChild(createDivEl()); }}
        }}
        
        if(typeof updateTerminalStyle === 'function') updateTerminalStyle();
    }})()
    """
    page.runJavaScript(js)

def inject_terminal_001(page, x, y):
    term_css = """
div.terminal{
    border: 1px solid black;
    border: solid 3px #BBBBBB;
    border-radius: 16px;
    background-color: #000000;
/* 终端上方的黑色阴影 */
    background-image:
        radial-gradient(ellipse 1000% 100% at 50% 90%, transparent, #121);
    background-position: center;
    display: block;
/* 终端周围的阴影 */
    box-shadow: inset 0 0 10em 1em rgba(0,0,0,0.5);
/* 防止扫描条产生滚动条 */
    overflow:hidden;
}
div.terminal blockquote {
    background-color: black;
    border: double 3px #80FF80;
    color: #80FF80;
}
div.scanline{
    margin-top: -40%;
    width: 100%;
    height: 60px;
    position: relative;
    pointer-events: none;
/* Safari 4.0 - 8.0 */
    -webkit-animation: scan 12s linear 0s infinite; 
    animation: scan 12s linear 0s infinite; 
    background: linear-gradient(to bottom, rgba(56, 112, 82,0), rgba(56, 112, 82,0.1)) !important;
}

div.text{
    color: rgba(128,255,128,0.8);
    padding-left: 2em;
    padding-top: 40%;
    font-family: 'Courier New', monospace;
    font-size: 1.2em;
    }

/* Safari 4.0 - 8.0 */
@-webkit-keyframes scan{
    from{ transform: translateY(-10%);}
    to{  transform: translateY(5000%);} 
}

@keyframes scan{
    from{ transform: translateY(-10%);}
    to{  transform: translateY(5000%);} 
}

div.text a {
    color: #90EE90;
    text-decoration: none;
    background: transparent;
}
div.text a.newpage {
    color: #90EE90;
    text-decoration: none;
    background: transparent;
}
div.text a:hover {
    color: #131;
    text-decoration: underline;
    background-color: #80FF80;
    padding: 1px;
}
div.text a:hover::before{
content: "> ";
}
"""
    term_html = """<div class="scp-component div-box terminal" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="terminal"</div><div class="div-content" contenteditable="true"><div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="scanline"</div><div class="div-content" contenteditable="true"></div></div><div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="text"</div><div class="div-content" contenteditable="true"><div style="text-align: center;"><span style="font-size: 150%;"><u>终端 #001</u></span><br><p><br></p><p><br></p><span class="terminal-hr">------</span><br>欢迎，用户<br><span class="terminal-hr">------</span><br></div><p><br></p><p><br></p><p><br></p><blockquote>终端内部的链接会在鼠标移过时显示“&gt;”。<br><a href="http://www.baidu.com">就像这样</a></blockquote><br>谢谢你查看我的格式！<br><p><br></p><p><br></p></div></div></div></div>"""

    safe_css = term_css.replace('\n', '\\n').replace('"', '\\"')
    safe_html_js = term_html.replace('\n', '\\n').replace('"', '\\"')

    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component') : null;
        var type = comp ? comp.getAttribute('data-type') : null;

        var cssContent = "{safe_css}";
        var divHtml = '{safe_html_js}';
        
        function createCssEl() {{
            var box = document.createElement('div');
            box.className = 'scp-component css-box';
            box.setAttribute('data-type', 'css-module');
            box.setAttribute('contenteditable', 'false');
            box.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal #001) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
            return box;
        }}
        
        function createDivEl() {{
            return document.createRange().createContextualFragment(divHtml);
        }}
        
        function hasTerminalCss() {{
             var css = document.querySelectorAll('.css-box .css-content');
             for(var i=0; i<css.length; i++) {{
                 if(css[i].innerText.indexOf('.danke') !== -1 && css[i].innerText.indexOf('.agent') !== -1) return true;
             }}
             return false;
        }}

        if (type === 'css-module') {{
            comp.innerHTML = '<details open><summary class="css-header" style=" user-select:none;">CSS Module (Terminal #001) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
            var next = comp.nextElementSibling;
            var needDiv = true;
            if (next && next.classList.contains('div-box')) {{
                var header = next.querySelector('.div-header');
                if (header && header.innerText.indexOf('terminal') !== -1) {{ needDiv = false; }}
            }}
            if (needDiv) {{ comp.parentNode.insertBefore(createDivEl(), comp.nextSibling); }}
        }} else if (type === 'div-block') {{
            var newDiv = createDivEl();
            comp.parentNode.replaceChild(newDiv, comp);
            if (!hasTerminalCss()) {{ editor.insertBefore(createCssEl(), editor.firstChild); }}
        }} else {{
            if (!hasTerminalCss()) {{ editor.insertBefore(createCssEl(), editor.firstChild); }}
            if (comp) {{
                 var newDiv = createDivEl();
                 comp.parentNode.insertBefore(newDiv, comp.nextSibling);
            }} else {{ editor.appendChild(createDivEl()); }}
        }}
        
        if(typeof updateTerminalStyle === 'function') updateTerminalStyle();
    }})();
    """
    page.runJavaScript(js)

def inject_raisa_notice(page, x, y):
    style = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5;"
    js = f"""
    (function() {{
        try {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({x}, {y});
            var comp = null;
            
            if (el) {{
                comp = el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box');
            }}
            
            if (!comp) {{
                 var sel = window.getSelection();
                 if (sel.rangeCount > 0) {{
                     var range = sel.getRangeAt(0);
                     var node = range.startContainer;
                     if (node.nodeType === 3) node = node.parentNode;
                     if (node) comp = node.closest('.scp-component');
                 }}
            }}

            var divBox = document.createElement('div');
            divBox.className = 'scp-component raisa-box'; 
            divBox.setAttribute('data-type', 'raisa-notice');
            divBox.setAttribute('contenteditable', 'false');
            divBox.style.cssText = "{style} position: relative; clear: both;";
            
            var divContent = document.createElement('div');
            divContent.className = 'raisa-content';
            divContent.setAttribute('contenteditable', 'true');
            
            var centerDiv = document.createElement('div');
            centerDiv.style.textAlign = 'center';
            centerDiv.className = 'raisa-inner';
            
            var titleSpan = document.createElement('span');
            titleSpan.style.fontSize = 'larger';
            var strong = document.createElement('strong');
            strong.innerText = '基金会记录与信息安全管理部的通知';
            titleSpan.appendChild(strong);
            
            centerDiv.appendChild(titleSpan);
            centerDiv.appendChild(document.createElement('br'));
            centerDiv.appendChild(document.createElement('br'));
            
            centerDiv.appendChild(document.createTextNode('通知在此'));
            centerDiv.appendChild(document.createElement('br'));
            centerDiv.appendChild(document.createElement('br'));
            centerDiv.appendChild(document.createTextNode('— Maria Jones，RAISA主管'));
            
            divContent.appendChild(centerDiv);
            divBox.appendChild(divContent);
            
            if (comp) {{
                if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                    comp.parentNode.replaceChild(divBox, comp);
                }} else {{
                    comp.parentNode.insertBefore(divBox, comp.nextSibling);
                }}
            }} else {{
                if (editor) {{ editor.appendChild(divBox); }}
            }}
            
            var br = document.createElement('br');
            if (divBox.nextSibling) {{ divBox.parentNode.insertBefore(br, divBox.nextSibling); }} 
            else {{ divBox.parentNode.appendChild(br); }}
        }} catch(e) {{ console.error("Error applying RAISA notice:", e); }}
    }})();
    """
    page.runJavaScript(js)

def inject_class_warning(page, x, y):
    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box') : null;
        
        var divBox = document.createElement('div');
        divBox.className = 'scp-component class-warning-box'; 
        divBox.setAttribute('data-type', 'class-warning');
        divBox.setAttribute('contenteditable', 'false');
        
        var style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) center no-repeat; border: solid 2px #000; padding: 1px 15px; box-shadow: 0 1px 3px rgba(0,0,0,.2); margin: 10px auto; width: fit-content;";
        divBox.style.cssText = style + " position: relative; clear: both;";
        
        var divContent = document.createElement('div');
        divContent.className = 'class-warning-content';
        divContent.setAttribute('contenteditable', 'true');
        
        var centerDiv = document.createElement('div');
        centerDiv.style.textAlign = 'center';
        centerDiv.className = 'class-warning-inner';
        
        var span1 = document.createElement('span');
        span1.style.color = 'rgb(255, 92, 72)';
        var span2 = document.createElement('span');
        span2.style.fontSize = '150%';
        var strong1 = document.createElement('strong');
        strong1.textContent = '警告：下列文件为#/XXXX级机密';
        span2.appendChild(strong1);
        span1.appendChild(span2);
        centerDiv.appendChild(span1);
        
        var hr = document.createElement('hr');
        hr.className = 'class-warning-hr'; 
        hr.style.border = 'none';
        hr.style.borderTop = '1px solid #777'; 
        hr.style.margin = '10px 0';
        centerDiv.appendChild(hr);
        
        var span3 = document.createElement('span');
        span3.style.fontSize = 'larger';
        var strong2 = document.createElement('strong');
        strong2.textContent = '无#/XXXX级权限下访问将被记录并立即处以纪律处分。';
        span3.appendChild(strong2);
        centerDiv.appendChild(span3);
        
        divContent.appendChild(centerDiv);
        divBox.appendChild(divContent);
        
        if (comp) {{
            if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                comp.parentNode.replaceChild(divBox, comp);
            }} else {{
                comp.parentNode.insertBefore(divBox, comp.nextSibling);
            }}
        }} else {{
            editor.appendChild(divBox);
        }}
        
        var br = document.createElement('br');
        if (divBox.nextSibling) {{ divBox.parentNode.insertBefore(br, divBox.nextSibling); }} 
        else {{ divBox.parentNode.appendChild(br); }}
    }})();
    """
    page.runJavaScript(js)

def inject_foundation_background(page, x, y):
    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
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
        
        if (comp) {{
            if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                comp.parentNode.replaceChild(divBox, comp);
            }} else {{
                comp.parentNode.insertBefore(divBox, comp.nextSibling);
            }}
        }} else {{
            editor.appendChild(divBox);
        }}
        
        var endP = document.createElement('p');
        endP.innerHTML = '<br>';
        if (divBox.nextSibling) {{
             divBox.parentNode.insertBefore(endP, divBox.nextSibling);
        }} else {{
             divBox.parentNode.appendChild(endP);
        }}
    }})();
    """
    page.runJavaScript(js)

def inject_o5_command(page, x, y):
    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;
        
        var divBox = document.createElement('div');
        divBox.className = 'scp-component o5-box'; 
        divBox.setAttribute('data-type', 'o5-command');
        divBox.setAttribute('contenteditable', 'false');
        
        var style = "background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px;";
        divBox.style.cssText = style + " position: relative; clear: both;";
        
        var divContent = document.createElement('div');
        divContent.className = 'o5-content';
        divContent.setAttribute('contenteditable', 'true');
        divContent.style.paddingTop = '80px';
        divContent.style.paddingBottom = '40px';
        
        var centerDiv = document.createElement('div');
        centerDiv.style.textAlign = 'center';
        centerDiv.className = 'o5-center-block';
        
        var h2 = document.createElement('h2');
        h2.className = 'o5-h2';
        h2.style.margin = '0';
        var span1 = document.createElement('span');
        span1.style.color = 'black';
        var strong1 = document.createElement('strong');
        strong1.textContent = '根据监督者议会的命令';
        span1.appendChild(strong1);
        h2.appendChild(span1);
        centerDiv.appendChild(h2);
        
        var p2 = document.createElement('div');
        p2.className = 'o5-p';
        var span2 = document.createElement('span');
        span2.style.color = 'black';
        span2.textContent = '以下文件为X/XXXX级机密。禁止未经授权的访问。';
        p2.appendChild(span2);
        centerDiv.appendChild(p2);
        
        divContent.appendChild(centerDiv);
        
        var h1 = document.createElement('h1');
        h1.className = 'o5-h1';
        h1.style.textAlign = 'center';
        var span3 = document.createElement('span');
        span3.style.color = 'black';
        var strong3 = document.createElement('strong');
        strong3.textContent = 'XXXX';
        span3.appendChild(strong3);
        h1.appendChild(span3);
        divContent.appendChild(h1);

        divBox.appendChild(divContent);
        
        if (comp) {{
            if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                comp.parentNode.replaceChild(divBox, comp);
            }} else {{ comp.parentNode.insertBefore(divBox, comp.nextSibling); }}
        }} else {{ editor.appendChild(divBox); }}
        
        var br = document.createElement('br');
        if (divBox.nextSibling) {{ divBox.parentNode.insertBefore(br, divBox.nextSibling); }} 
        else {{ divBox.parentNode.appendChild(br); }}
    }})();
    """
    page.runJavaScript(js)

def inject_video_record(page, x, y):
    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component') : null;

        var divBox = document.createElement('div');
        divBox.className = 'scp-component div-box';
        divBox.setAttribute('data-type', 'div-block');
        divBox.setAttribute('contenteditable', 'false');
        divBox.style.cssText = 'position: relative; clear: both;';

        var divHeader = document.createElement('div');
        divHeader.className = 'div-header';
        divHeader.setAttribute('contenteditable', 'true');
        divHeader.setAttribute('onclick', 'toggleDiv(this)');
        divHeader.style.cssText = '';
        divHeader.title = '点击折叠/展开';
        divHeader.textContent = 'DIV: class="blockquote"';
        divBox.appendChild(divHeader);

        var divContent = document.createElement('div');
        divContent.className = 'div-content';
        divContent.setAttribute('contenteditable', 'true');
        divContent.innerHTML = [
            '<div style="text-align:center;"><b>\u89c6\u9891\u8bb0\u5f55</b></div>',
            '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
            '<p><b>\u65e5\u671f\uff1a</b></p>',
            '<p><b>\u7b14\u8bb0\uff1a</b></p>',
            '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
            '<p>[\u8bb0\u5f55\u5f00\u59cb]</p>',
            '<p><b>\u65f6\u95f4\uff1a</b>\u4e8b\u4ef6</p>',
            '<p><b>\u65f6\u95f4\uff1a</b>\u4e8b\u4ef6</p>',
            '<p><b>\u65f6\u95f4\uff1a</b>\u4e8b\u4ef6</p>',
            '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
            '<p>[\u8bb0\u5f55\u7ed3\u675f]</p>'
        ].join('');
        divBox.appendChild(divContent);

        if (comp) {{
            if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                comp.parentNode.replaceChild(divBox, comp);
            }} else {{ comp.parentNode.insertBefore(divBox, comp.nextSibling); }}
        }} else {{ editor.appendChild(divBox); }}

        var br = document.createElement('br');
        if (divBox.nextSibling) {{ divBox.parentNode.insertBefore(br, divBox.nextSibling); }} 
        else {{ divBox.parentNode.appendChild(br); }}
    }})();
    """
    page.runJavaScript(js)

def inject_video_record2(page, x, y):
    params = 'class="blockquote" style="border-radius: 10px; margin: 10px"'
    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component') : null;

        var divBox = document.createElement('div');
        divBox.className = 'scp-component div-box';
        divBox.setAttribute('data-type', 'div-block');
        divBox.setAttribute('contenteditable', 'false');
        divBox.style.cssText = 'border-radius: 10px; margin: 10px; position: relative; clear: both;';

        var divHeader = document.createElement('div');
        divHeader.className = 'div-header';
        divHeader.setAttribute('contenteditable', 'true');
        divHeader.setAttribute('onclick', 'toggleDiv(this)');
        divHeader.style.cssText = '';
        divHeader.title = '\u70b9\u51fb\u6298\u53e0/\u5c55\u5f00';
        divHeader.textContent = 'DIV: {params}';
        divBox.appendChild(divHeader);

        var divContent = document.createElement('div');
        divContent.className = 'div-content';
        divContent.setAttribute('contenteditable', 'true');
        divContent.innerHTML = [
            '<p><b>\u89c6\u9891\u65e5\u5fd7\u8bb0\u5f55</b></p>',
            '<p><b>\u65e5\u671f\uff1a</b>\u53ef\u9009</p>',
            '<p><b>\u63a2\u7d22\u961f\u4f0d\uff1a</b>\u961f\u4f0d\u540d\u79f0 - \u53ef\u9009</p>',
            '<p><b>\u76ee\u6807\uff1a</b>\u533a\u57df/\u5f02\u5e38 - \u53ef\u9009</p>',
            '<p><b>\u9886\u961f\uff1a</b>\u53ef\u9009</p>',
            '<p><b>\u5c0f\u961f\u6210\u5458\uff1a</b>\u53ef\u9009</p>',
            '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
            '<p>[\u8bb0\u5f55\u5f00\u59cb]</p>',
            '<p><b>\u4eba\u7269A\uff1a</b>\u5bf9\u767d</p>',
            '<p><b>\u4eba\u7269B\uff1a</b>\u5bf9\u767d</p>',
            '<p><i>\u4e8b\u4ef6\u53d1\u751f</i></p>',
            '<p><b>\u4eba\u7269A\uff1a</b>\u5bf9\u767d</p>',
            '<p>[\u8bb0\u5f55\u7ed3\u675f]</p>'
        ].join('');
        divBox.appendChild(divContent);

        if (comp) {{
            if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                comp.parentNode.replaceChild(divBox, comp);
            }} else {{ comp.parentNode.insertBefore(divBox, comp.nextSibling); }}
        }} else {{ editor.appendChild(divBox); }}

        var br = document.createElement('br');
        if (divBox.nextSibling) {{ divBox.parentNode.insertBefore(br, divBox.nextSibling); }} 
        else {{ divBox.parentNode.appendChild(br); }}
    }})();
    """
    page.runJavaScript(js)

def inject_page_note(page, x, y):
    page_style = (
        'display:block; overflow:hidden; '
        'font-family:"Monotype Corsiva","Bradley Hand ITC",sans-serif; '
        'background-attachment:scroll; '
        'background-image:linear-gradient(to top,rgb(202,219,228) 0%,rgb(231,233,220) 8%); '
        'background-position:0px 8px; background-repeat:repeat; background-size:100% 20px; '
        'border:1px solid #CCC; border-radius:10px; padding:10px; margin-bottom:10px; '
        'box-shadow:0px 1px 3px rgba(0,0,0,0.2); position:relative; clear:both;'
    )
    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;

        var box = document.createElement('div');
        box.className = 'scp-component page-note-box';
        box.setAttribute('data-type', 'page-note');
        box.setAttribute('contenteditable', 'false');
        box.style.cssText = '{page_style}';

        var label = document.createElement('div');
        label.className = 'page-note-label';
        label.setAttribute('contenteditable', 'false');
        label.style.cssText = 'font-size:10px;color:#aaa;text-align:right;margin-bottom:2px;';
        label.textContent = '\u4fbf\u7b7e\u7eb8';
        box.appendChild(label);

        var content = document.createElement('div');
        content.className = 'page-note-content';
        content.setAttribute('contenteditable', 'true');
        content.style.cssText = "font-family:'Monotype Corsiva','Bradley Hand ITC',sans-serif;line-height:20px;";
        content.innerHTML = [
            '<p>\u6b63\u6587\u5728\u6b64\u3002</p>',
            '<p><br></p>',
            '<p>\u5c31\u50cf\u8fd9\u6837\u3002</p>'
        ].join('');
        box.appendChild(content);

        if (comp) {{
            if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                comp.parentNode.replaceChild(box, comp);
            }} else {{ comp.parentNode.insertBefore(box, comp.nextSibling); }}
        }} else {{
            if (editor) {{ editor.appendChild(box); }}
        }}
        
        var br = document.createElement('br');
        if (box.nextSibling) {{ box.parentNode.insertBefore(br, box.nextSibling); }} 
        else {{ box.parentNode.appendChild(br); }}
    }})();
    """
    page.runJavaScript(js)

def inject_email_template(page, x, y):
    js = f"""
    (function() {{
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;
        
        var divBox = document.createElement('div');
        divBox.className = 'scp-component email-example-box'; 
        divBox.setAttribute('data-type', 'email-example');
        divBox.setAttribute('contenteditable', 'false');
        divBox.style.border = '2px dashed #ccc';
        divBox.style.padding = '10px';
        divBox.style.margin = '20px 0';
        divBox.style.background = '#fdfdfd';
        
        var html = `
        <div style="border-bottom: 1px solid #999; margin-bottom: 10px; text-align: left;">
            <span class="email-show-title" contenteditable="true" style="color:#b01; font-weight:bold; ">访问SCiPNET邮件？一 (1) 封新邮件！</span>
            <span style="color:#888; margin-left:10px; font-size: 12px;">(展开标题 - 点击编辑)</span>
            <br>
            <span class="email-hide-title" contenteditable="true" style="color:#b01; font-weight:bold; ">回复：主题</span>
            <span style="color:#888; margin-left:10px; font-size: 12px;">(折叠标题 - 点击编辑)</span>
        </div>
        <div class="email-item" style="border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px auto; box-shadow: 0 1px 3px rgba(0,0,0,.5); text-align: left; background: #fff;">
            <div class="tofrom" style="margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon; text-align: left;">
                <b>至：</b><span class="email-to1" contenteditable="true">收件人</span><br>
                <b>自：</b><span class="email-from1" contenteditable="true">发件人</span><br>
                <b>主题：</b><span class="email-subj1" contenteditable="true">主题</span>
            </div>
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 10px 0;">
            <div class="email-content1" contenteditable="true" style="min-height: 30px;">文本</div>
        </div>
        <div style="text-align: center; color: #888; margin: 10px 0;">@@ @@</div>
        <div class="email-item" style="border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px auto; box-shadow: 0 1px 3px rgba(0,0,0,.5); text-align: left; background: #fff;">
            <div class="tofrom" style="margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon; text-align: left;">
                <b>至：</b><span class="email-to2" contenteditable="true">收件人</span><br>
                <b>自：</b><span class="email-from2" contenteditable="true">发件人</span><br>
                <b>主题：</b><span class="email-subj2" contenteditable="true">回复：主题</span>
            </div>
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 10px 0;">
            <div class="email-content2" contenteditable="true" style="min-height: 30px;">文本</div>
        </div>
        <div class="email-css-indicator" contenteditable="false" style="background-color:#f0f0f0;border:1px solid #ccc;padding:5px;margin-top:10px;font-size:12px;color:#666;font-family:monospace;text-align:left;"><i>[CSS模块已折叠连体，导出时将自动附带相应的格式代码及水平线居中排列]</i></div>
        `;
        
        divBox.innerHTML = html;
        
        if (comp) {{ comp.parentNode.insertBefore(divBox, comp); }} 
        else {{ document.getElementById('editor-root').appendChild(divBox); }}
        
        var br = document.createElement('p');
        br.innerHTML = '<br>';
        divBox.parentNode.insertBefore(br, divBox.nextSibling);
    }})();
    """
    page.runJavaScript(js)

def inject_login_logout(page, x, y):
    js = f"""
    (function() {{
        var editor = document.getElementById('editor-root');
        var el = document.elementFromPoint({x}, {y});
        var comp = el ? el.closest('.scp-component') : null;

        var box = document.createElement('div');
        box.className = 'scp-component login-logout-box';
        box.setAttribute('data-type', 'login-logout');
        box.setAttribute('contenteditable', 'false');
        box.style.cssText = 'border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;';

        var tbl = document.createElement('table');
        tbl.className = 'login-form-table';
        tbl.setAttribute('contenteditable', 'false');
        tbl.style.cssText = 'margin:0.5em auto; border-collapse:collapse;';

        var tr1 = document.createElement('tr');
        var td1a = document.createElement('td');
        td1a.style.cssText = 'width:80px; padding:4px 8px; font-family:sans-serif;';
        td1a.setAttribute('contenteditable', 'false');
        td1a.textContent = 'ID';
        var td1b = document.createElement('td');
        var idInput = document.createElement('span');
        idInput.className = 'login-id-value';
        idInput.setAttribute('contenteditable', 'true');
        idInput.style.cssText = 'display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;';
        idInput.textContent = '\u4f60\u7684ID';
        td1b.appendChild(idInput);
        tr1.appendChild(td1a); tr1.appendChild(td1b);

        var tr2 = document.createElement('tr');
        var td2a = document.createElement('td');
        td2a.style.cssText = 'width:80px; padding:4px 8px; font-family:sans-serif;';
        td2a.setAttribute('contenteditable', 'false');
        td2a.textContent = '\u5bc6\u7801';
        var td2b = document.createElement('td');
        var pwSpan = document.createElement('span');
        pwSpan.setAttribute('contenteditable', 'false');
        pwSpan.style.cssText = 'display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif; color:#555; letter-spacing:2px;';
        pwSpan.textContent = '\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb';
        td2b.appendChild(pwSpan);
        tr2.appendChild(td2a); tr2.appendChild(td2b);

        var tr3 = document.createElement('tr');
        var td3a = document.createElement('td');
        td3a.setAttribute('contenteditable', 'false');
        var td3b = document.createElement('td');
        td3b.style.textAlign = 'center';
        td3b.setAttribute('contenteditable', 'false');
        var btn = document.createElement('button');
        btn.setAttribute('contenteditable', 'false');
        btn.style.cssText = 'padding:2px 18px; border:1px solid #aaa; background:#f4f4f4;  font-family:sans-serif;';
        btn.textContent = '\u767b\u5165';
        td3b.appendChild(btn);
        tr3.appendChild(td3a); tr3.appendChild(td3b);

        tbl.appendChild(tr1); tbl.appendChild(tr2); tbl.appendChild(tr3);
        box.appendChild(tbl);

        var sep = document.createElement('hr');
        sep.setAttribute('contenteditable', 'false');
        sep.style.cssText = 'border:none; border-top:1px solid #ccc; margin:6px 0;';
        box.appendChild(sep);

        var lbl = document.createElement('div');
        lbl.setAttribute('contenteditable', 'false');
        lbl.style.cssText = 'font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;';
        lbl.textContent = '[\u767b\u5165]\u2194[\u767b\u51fa] \u6298\u53e0\u5185\u5bb9';
        box.appendChild(lbl);

        var content = document.createElement('div');
        content.className = 'login-collapsible-content';
        content.setAttribute('contenteditable', 'true');
        content.style.cssText = 'min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;';
        content.innerHTML = '<p>\u6587\u5b57</p>';
        box.appendChild(content);

        if (comp) {{ comp.parentNode.insertBefore(box, comp.nextSibling); }} 
        else {{ editor.appendChild(box); }}
        
        var br = document.createElement('br');
        box.parentNode.insertBefore(br, box.nextSibling);
    }})();
    """
    page.runJavaScript(js)