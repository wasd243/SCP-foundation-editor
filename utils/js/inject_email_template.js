(function () {
    var el = document.elementFromPoint(__POS_X__, __POS_Y__);
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

    if (comp) { comp.parentNode.insertBefore(divBox, comp); }
    else { document.getElementById('editor-root').appendChild(divBox); }

    var br = document.createElement('p');
    br.innerHTML = '<br>';
    divBox.parentNode.insertBefore(br, divBox.nextSibling);
})();