import re
import html as _html_module

def parse_wikidot_code(code: str) -> dict:
    """提取侧边栏/主题属性等元数据"""
    result = {
        "themes": {
            "basalt": False, "basalt_dark": False, "basalt_wide": False, "basalt_hidetitle": False,
            "shivering_night": False, "shivering_sub": "default",
            "bhl": False, "bhl_dark_sidebar": False, "bhl_collapsible": False, "bhl_toggle": False, "bhl_centered": False, "bhl_office": False,
        },
        "better_footnotes": False,
        "rate_module": {"hidden": True, "align": ""},
        "css": ""
    }

    if not code or not code.strip():
        return result

    if "theme:basalt" in code:
        result["themes"]["basalt"] = True
        if "darkmode=a" in code: result["themes"]["basalt_dark"] = True
        if "wide=a" in code: result["themes"]["basalt_wide"] = True
        if "hidetitle=a" in code: result["themes"]["basalt_hidetitle"] = True
    elif "theme:shivering-night" in code:
        result["themes"]["shivering_night"] = True
        if "theme:shivering-night-macau" in code: result["themes"]["shivering_sub"] = "macau"
        elif "theme:shivering-night-kuala-lumpur" in code: result["themes"]["shivering_sub"] = "kl"
        elif "theme:shivering-night-dublin" in code: result["themes"]["shivering_sub"] = "dub"
        elif "theme:shivering-night-cape-town" in code: result["themes"]["shivering_sub"] = "ct"
        elif "theme:shivering-night-buenos-aires" in code: result["themes"]["shivering_sub"] = "ba"
    elif "theme:black-highlighter-theme" in code:
        result["themes"]["bhl"] = True
        if ":component:bhl-dark-sidebar" in code: result["themes"]["bhl_dark_sidebar"] = True
        if ":component:collapsible-sidebar" in code: result["themes"]["bhl_collapsible"] = True
        if ":component:toggle-sidebar-bhl" in code: result["themes"]["bhl_toggle"] = True
        if ":component:centered-header-bhl" in code: result["themes"]["bhl_centered"] = True
        if "theme:scp-offices-theme" in code: result["themes"]["bhl_office"] = True

    if ":component:betterfootnotes" in code:
        result["better_footnotes"] = True

    if re.search(r'\[\[module Rate\]\]', code, re.IGNORECASE):
        result["rate_module"]["hidden"] = False
        if re.search(r'\[\[<\]\]\s*\[\[module Rate\]\]\s*\[\[/<\]\]', code, re.IGNORECASE):
             result["rate_module"]["align"] = "left"
        elif re.search(r'\[\[>\]\]\s*\[\[module Rate\]\]\s*\[\[/>\]\]', code, re.IGNORECASE):
             result["rate_module"]["align"] = "right"

    extracted_css = ""
    css_matches = re.finditer(r'\[\[module CSS\]\](.*?)\[\[/module\]\]', code, flags=re.DOTALL|re.IGNORECASE)
    for m in css_matches:
        extracted_css += m.group(1).strip() + "\n"

    if ".danke" in extracted_css and ".agent" in extracted_css:
        extracted_css += """
        /* Force Terminal Style for all DIV modules in Editor View */
        .div-box { background-color: #000000 !important; border: 2px solid #55AA55 !important; color: #77CC77 !important; font-family: 'Courier New', monospace !important; }
        .div-header { background-color: #55AA55 !important; color: #002200 !important; border-bottom: 1px solid #002200 !important; font-weight: bold; }
        .div-content { background-color: #000000 !important; color: #77CC77 !important; }
        """
        
    result["css"] = extracted_css
    return result


def parse_wikidot_to_editor_html(text: str, theme_type: str = "none") -> str:
    """
    核心反向解析器（完美保留你的原版逻辑，仅去除了 self 依赖）
    """
    text = _html_module.unescape(text)
    text = re.sub(r'<p>\s*<br\s*/?>\s*</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
    _has_basalt_in_source = (
        ":theme:basalt" in text.lower() or 
        "theme='basalt'" in text.lower() or 
        'theme="basalt"' in text.lower()
    )
    
    placeholders = {}
    ph_count = 0
    def register_ph(html_content):
        nonlocal ph_count
        token = f"_WIKIDOT_PH_{ph_count}_"
        placeholders[token] = html_content
        ph_count += 1
        return token

    def register_forced_break(source):
        html = f'<p class="forced-break" data-source="{source}" contenteditable="false" style="display: block; width: 100%; height: 0em; min-height: 0; border: 1px dashed transparent; margin: 0;"></p>'
        return register_ph(html)

    def process_terminal_source(txt):
        pattern_start = re.compile(r'\[\[div\s+class="terminal"\]\]', re.IGNORECASE)
        pattern_end = re.compile(r'\[\[/div\]\]', re.IGNORECASE)
        
        result = []
        current_pos = 0
        
        matches = list(pattern_start.finditer(txt))
        if not matches:
            return txt.replace('@@ @@', register_forced_break('@@ @@')).replace('@@@@', register_forced_break('@@@@'))
        
        last_end = 0
        new_text = ""
        valid_ranges = []
        
        for m in matches:
            start = m.end()
            bracket_start = m.start()
            if bracket_start < last_end: continue 
            
            depth = 1
            search_pos = start
            
            while depth > 0:
                next_open = re.search(r'\[\[div.*?\]\]', txt[search_pos:], re.IGNORECASE)
                next_close = pattern_end.search(txt[search_pos:])
                if not next_close: break
                pos_close = search_pos + next_close.start()
                pos_open = search_pos + next_open.start() if next_open else -1
                
                if next_open and pos_open < pos_close:
                    depth += 1
                    search_pos = pos_open + (next_open.end() - next_open.start())
                else:
                    depth -= 1
                    search_pos = pos_close + 8 
                    
            if depth == 0:
                valid_ranges.append((bracket_start, search_pos))
                last_end = search_pos
        
        curr = 0
        for start, end in valid_ranges:
            new_text += txt[curr:start].replace('@@ @@', register_forced_break('@@ @@')).replace('@@@@', register_forced_break('@@@@'))
            raw_block = txt[start:end]
            header_match = pattern_start.match(raw_block)
            header_len = header_match.end()
            footer_len = 8
            inner_content = raw_block[header_len:-footer_len]
            
            def escape_wiki(t):
                ph_divs = []
                def div_hide(m):
                    ph_divs.append(m.group(0))
                    return f"__DIV_PH_{len(ph_divs)-1}__"
                t = re.sub(r'\[\[/?div.*?\]\]', div_hide, t, flags=re.IGNORECASE)
                t = t.replace('[[', '&#91;&#91;').replace(']]', '&#93;&#93;')
                def div_restore(m):
                    idx = int(m.group(1))
                    return ph_divs[idx]
                t = re.sub(r'__DIV_PH_(\d+)__', div_restore, t)
                return t

            processed_inner = escape_wiki(inner_content)
            processed_inner = processed_inner.replace('@@ @@', register_forced_break('@@ @@')).replace('@@@@', register_forced_break('@@@@'))
            processed_inner = processed_inner.replace('@@------@@', '<span class="terminal-hr">------</span>')
            new_text += raw_block[:header_len] + processed_inner + raw_block[-footer_len:]
            curr = end
        
        new_text += txt[curr:].replace('@@ @@', register_forced_break('@@ @@')).replace('@@@@', register_forced_break('@@@@'))
        return new_text

    text = process_terminal_source(text)

    text = re.sub(r'\[\[<\]\]\s*\[\[module Rate\]\]\s*\[\[/<\]\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[>\]\]\s*\[\[module Rate\]\]\s*\[\[/>\]\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[module Rate\]\]', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\[\[include :scp-wiki-cn:theme:basalt.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[include :scp-wiki-cn:theme:shivering-night.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[include :scp-wiki-cn:theme:black-highlighter-theme.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\[\[include :scp-wiki:component:bhl-dark-sidebar.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[include :scp-wiki:component:collapsible-sidebar.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[include :scp-wiki:component:toggle-sidebar-bhl.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[include :scp-wiki:component:centered-header-bhl.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[include :scp-wiki-cn:theme:scp-offices-theme.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[include :scp-wiki-cn:component:betterfootnotes.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[footnoteblock\]\]\r?\n?', '', text, flags=re.IGNORECASE)
    
    license_phs = []
    def license_replacer(match):
        full_block = match.group(0)
        author_m = re.search(r'\|author=([^\|\n\]]+)', full_block)
        translator_m = re.search(r'\|translator=([^\|\n\]]+)', full_block)
        lang_m = re.search(r'\|lang=CN', full_block, re.IGNORECASE)
        author = author_m.group(1).strip() if author_m else ""
        translator = translator_m.group(1).strip() if translator_m else ""
        is_original = lang_m is not None
        
        files_content_im = re.search(r'=====(.*?)=====', full_block, flags=re.DOTALL)
        files_html = ""
        
        if files_content_im:
            file_text = files_content_im.group(1).strip()
            lines = file_text.split('\n')
            current_file = {}
            files_data = []
            
            def flush_file():
                if current_file:
                    files_data.append(current_file.copy())
                    current_file.clear()

            for line in lines:
                line = line.strip()
                if not line.startswith('>'): continue
                content = line[1:].strip()
                if content.startswith('**文件名：**'):
                    flush_file() 
                    current_file['file_name'] = content.replace('**文件名：**', '').strip()
                elif content.startswith('**图像名：**'):
                     current_file['img_name'] = content.replace('**图像名：**', '').strip()
                elif content.startswith('**图像作者：**'):
                     current_file['img_author'] = content.replace('**图像作者：**', '').strip()
                elif content.startswith('**作者：**'):
                     current_file['img_author'] = content.replace('**作者：**', '').strip()
                elif content.startswith('**授权协议：**'):
                     current_file['img_license'] = content.replace('**授权协议：**', '').strip()
                elif content.startswith('**来源链接：**'):
                     current_file['source_link'] = content.replace('**来源链接：**', '').strip()
                elif content.startswith('来源链接：'):
                     current_file['source_link'] = content.replace('来源链接：', '').strip()
                elif content.startswith('**衍生自：**'):
                     current_file['derived_from'] = content.replace('**衍生自：**', '').strip()
                elif content.startswith('**备注：**'):
                     current_file['note'] = content.replace('**备注：**', '').strip()
            
            flush_file() 
            for f in files_data:
                files_html += f'<div class="file-entry"><button class="btn-del-file" onclick="this.parentElement.remove()">×</button>'
                files_html += f'<div class="license-field-row"><span class="field-label">文件名：</span><span class="editable-field" data-field="file_name" contenteditable="true">{f.get("file_name", "")}</span></div>'
                files_html += f'<div class="license-field-row"><span class="field-label">图像名：</span><span class="editable-field" data-field="img_name" contenteditable="true">{f.get("img_name", "")}</span></div>'
                files_html += f'<div class="license-field-row"><span class="field-label">图像作者：</span><span class="editable-field" data-field="img_author" contenteditable="true">{f.get("img_author", "")}</span></div>'
                files_html += f'<div class="license-field-row"><span class="field-label">授权协议：</span><span class="editable-field" data-field="img_license" contenteditable="true">{f.get("img_license", "")}</span></div>'
                files_html += f'<div class="license-field-row license-link-row"><span class="field-label">来源链接：</span><span class="editable-field" data-field="source_link" contenteditable="false" onclick="editLicenseLink(this)">{f.get("source_link", "")}</span></div>'
                files_html += f'<div class="license-field-row"><span class="field-label">衍生自：</span><span class="editable-field" data-field="derived_from" contenteditable="true" style="word-break: break-all;">{f.get("derived_from", "")}</span></div>'
                files_html += f'<div class="license-field-row"><span class="field-label">备注：</span><span class="editable-field" data-field="note" contenteditable="true">{f.get("note", "")}</span></div>'
                files_html += '</div>'

        orig_attr = 'true' if is_original else 'false'
        orig_btn_cls = ' active' if is_original else ''
        trans_row_cls = ' disabled' if is_original else ''
        html = f'''<div class="scp-component license-box open" data-type="license" data-original="{orig_attr}" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)<button class="btn-license-original{orig_btn_cls}" onclick="toggleLicenseOriginal(this, event)" title="原创：生成|lang=CN，并取消|translator">原创</button></div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true">{author}</span></div><div class="license-field-row license-translator-row{trans_row_cls}"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true">{translator}</span></div><hr><div class="extra-files-container">{files_html}</div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>'''
        ph = register_ph(html)
        license_phs.append(ph)
        return ""

    text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\].*?\[\[include :scp-wiki-cn:component:license-box-end\]\]', license_replacer, text, flags=re.DOTALL)
    text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box-end.*?\]\]', '', text)
    text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\]', '', text, flags=re.DOTALL)
    
    def acs_replacer(match):
        block = match.group(0)
        def get_arg(name):
            m = re.search(fr'(?:\||\s){name}=([^\|\n\]]+)', block)
            return m.group(1).strip() if m else ""
        
        item = get_arg('item-number')
        clr = get_arg('clearance')
        cnt = get_arg('container-class')
        color_map = {
            'safe': '#27ae60', 'euclid': '#f1c40f', 'keter': '#c0392b',
            'neutralized': '#7f8c8d', 'pending': '#bdc3c7', 
            'explained': '#95a5a6', 'esoteric': '#595959', '机密': '#595959'
        }
        color = color_map.get(cnt.lower(), '#595959')
        sec = get_arg('secondary-class')
        sec_icon = get_arg('secondary-icon')
        dsr = get_arg('disruption-class')
        rsk = get_arg('risk-class')
        anim_checked = 'checked' if 'component:acs-animation' in text else ''
        
        is_shiver = get_arg('data-shivering') == 'true'
        shiver_checked = 'checked' if is_shiver else ''
        
        html = f'''<div class="scp-component acs-box" data-type="acs" data-clearance="{clr}" data-container="{cnt}" data-secondary="{sec or 'none'}" data-disruption="{dsr}" data-risk="{rsk}" data-shivering="{str(is_shiver).lower()}" style="--acs-color: {color};" contenteditable="false"><div class="acs-header-row" contenteditable="false"><div class="acs-title">SCP-CN 异常分级栏</div><div class="acs-toggles"><div class="acs-anim-toggle"><span>动画:</span><label class="switch"><input type="checkbox" class="acs-anim-checkbox" {anim_checked}><span class="slider"></span></label></div><div class="acs-shiver-toggle"><span>夜琉璃适配:</span><label class="switch"><input type="checkbox" class="acs-shiver-checkbox" {shiver_checked}><span class="slider"></span></label></div></div><div class="acs-item-num" contenteditable="true" data-field="item-number">{item}</div></div><div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 10px;"><div><small style="color:#888; font-size:9px; text-transform:uppercase;">许可等级</small><br><b data-field="clearance" contenteditable="true">{clr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">项目等级</small><br><b data-field="container" style="color:var(--acs-color)" contenteditable="true">{cnt}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">次要等级</small><br><b data-field="secondary" contenteditable="true">{sec or "none"}</b><div style="font-size:0.8em; border-top:1px solid #ccc; margin-top:2px;">Icon: <span data-field="secondary-icon" contenteditable="true" style="min-width:20px; display:inline-block">{sec_icon}</span></div></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">扰动等级</small><br><b data-field="disruption" contenteditable="true">{dsr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">风险等级</small><br><b data-field="risk" contenteditable="true">{rsk}</b></div></div></div>'''
        return register_ph(html)

    text = re.sub(r'\[\[div class="Shivering-ACS"\]\]\s*(\[\[include :scp-wiki-cn:component:anomaly-class-bar-source.*?\]\])\s*\[\[/div\]\]', r'\1 |data-shivering=true', text, flags=re.DOTALL)
    text = re.sub(r'\[\[include :scp-wiki-cn:component:anomaly-class-bar-source.*?\]\]', acs_replacer, text, flags=re.DOTALL)
    text = re.sub(r'\[\[include :scp-wiki-cn:component:acs-animation\]\]', '', text)

    def aim_replacer(match):
        block = match.group(0)
        def get_arg(name):
            m = re.search(fr'(?:\||\s+)\s*{name}\s*=\s*([^\|\n\]]+)', block, re.IGNORECASE)
            return m.group(1).strip() if m else "???"
        
        blocks_arg = get_arg('blocks')
        row_style_top = 'display:none;' if blocks_arg == '!' else ''
        row_style_bottom = 'display:none;' if blocks_arg == '-' else ''
        
        val_xxxx = get_arg('XXXX')
        val_lv = get_arg('lv')
        val_cc = get_arg('cc')
        val_dc = get_arg('dc')
        val_site = get_arg('site')
        val_dir = get_arg('dir')
        val_head = get_arg('head')
        val_mtf = get_arg('mtf')
        
        html = f'''<div class="scp-component aim-box" data-type="aim" data-blocks="{blocks_arg}" contenteditable="false"><table class="aim-table"><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">项目编号</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">{val_xxxx}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">等级 / 公开</div><div class="aim-value" data-field="lv" contenteditable="true">{val_lv}</div></td></tr><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">收容等级</div><div class="aim-value" data-field="cc" contenteditable="true">{val_cc}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">扰动等级</div><div class="aim-value" data-field="dc" contenteditable="true">{val_dc}</div></td></tr><tr style="{row_style_bottom} text-align: center; background: #fafafa;"><td><div class="aim-label">负责站点</div><div class="aim-value" data-field="site" contenteditable="true">{val_site}</div></td><td><div class="aim-label">站点主管</div><div class="aim-value" data-field="dir" contenteditable="true">{val_dir}</div></td><td><div class="aim-label">首席研究员</div><div class="aim-value" data-field="head" contenteditable="true">{val_head}</div></td><td><div class="aim-label">指派特遣队</div><div class="aim-value" data-field="mtf" contenteditable="true">{val_mtf}</div></td></tr></table><div class="aim-footer">AIM Module</div></div>'''
        return register_ph(html)

    text = re.sub(r'\[\[include :scp-wiki-cn:component:advanced-information-methodology.*?\]\]', aim_replacer, text, flags=re.DOTALL)

    def centering_pre_processor(txt):
        def wrap_center(m):
            content = m.group(1)
            if re.search(r'align=[^|\]\n]+', content, re.IGNORECASE):
                content = re.sub(r'align=[^|\]\n]+', 'align=center', content, flags=re.IGNORECASE)
            else:
                content = content.replace(']]', ' |align=center]]')
            return content
        return re.sub(r'\[\[=\]\]\s*(\[\[include component:image-block.*?\]\])\s*\[\[/=\]\]', wrap_center, txt, flags=re.DOTALL | re.IGNORECASE)

    text = centering_pre_processor(text)

    def img_replacer(match):
        block = match.group(0)
        def get_arg(name): 
            m = re.search(fr'(?:\||\s+)\s*{name}\s*=\s*([^\|\n\]]+)', block, re.IGNORECASE)
            return m.group(1).strip() if m else ""
        name = get_arg('name')
        caption = get_arg('caption')
        width = get_arg('width')
        height = get_arg('height')
        align = get_arg('align') or 'right'
        c_type = "image-block-adv"
        
        img_style = "max-width:100%; display:block; margin:0 auto 5px auto;"
        if width:
            w = width.lower().strip()
            if w and not (w.endswith('px') or w.endswith('%')): w += "px"
            img_style += f" width:{w};"
        if height:
            h = height.lower().strip()
            if h and not (h.endswith('px') or h.endswith('%')): h += "px"
            img_style += f" height:{h};"
        
        if align == 'center':
            img_style += " width:100% !important;"

        dim_html = f'''<div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div style="display:flex; align-items:center;"><b style="flex-shrink:0;">源: &nbsp;</b><span data-field="name" style="display:none;">{name}</span><span class="img-link-label" onclick="editImgLink(this)" onmousedown="event.stopPropagation();" style="color:blue; text-decoration:underline; cursor:pointer;">链接</span></div><div style="display:flex; justify-content:space-between; align-items:baseline;"><span><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{width}</span></span> <span><b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{height}</span></span></div></div>'''

        html = f'''<div class="scp-component image-block-box" data-type="{c_type}" data-align="{align}" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'center')" onmousedown="event.stopPropagation();">置中</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div>{dim_html}</div><div class="image-block-content"><img src="{name}" class="img-preview" style="{img_style}"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;display:none;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">{caption}</span></div></div>'''
        return register_ph(html)

    text = re.sub(r'\[\[include component:image-block.*?\]\]', img_replacer, text, flags=re.DOTALL)

    def tabview_replacer(match):
        content = match.group(1)
        tabs = re.findall(r'\[\[tab ([^\]]+)\]\](.*?)\[\[/tab\]\]', content, flags=re.DOTALL)
        header_html = ""
        body_html = ""
        for i, (title, body) in enumerate(tabs):
            active = " active" if i == 0 else ""
            header_html += f'<span class="tab-btn{active}" onclick="selectTab(this)" contenteditable="true">{title.strip()}</span>'
            parsed_body = parse_wikidot_to_editor_html(body, theme_type)
            body_html += f'<div class="tab-item{active}" contenteditable="true">{parsed_body}</div>'
        html = f'''<div class="scp-component tabview-box" data-type="tabview" contenteditable="false"><div class="tab-header">{header_html}<span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents">{body_html}</div></div>'''
        return register_ph(html)
        
    text = re.sub(r'\[\[tabview\]\](.*?)\[\[/tabview\]\]', tabview_replacer, text, flags=re.DOTALL)

    _FAKEPROT_EARLY_SIG = '.fakeprot .mailform-box .buttons'
    if _FAKEPROT_EARLY_SIG in text:
        def process_fakeprot_source(txt):
            result = []
            cursor = 0
            pat_div_start = re.compile(
                r'\[\[div\s+class=["\']fakeprot["\']\]\]', re.IGNORECASE
            )
            pat_div_close = re.compile(r'\[\[/div\]\]', re.IGNORECASE)
            pat_coll = re.compile(
                r'\s*\[\[collapsible\s+show="([^"]*)"\s+hide="([^"]*)"\]\](.*?)\[\[/collapsible\]\]',
                re.DOTALL | re.IGNORECASE
            )

            for m_start in pat_div_start.finditer(txt):
                div_start = m_start.start()
                if div_start < cursor:
                    continue

                depth = 1
                i = m_start.end()
                div_end = None
                while i < len(txt) and depth > 0:
                    next_open = re.search(r'\[\[div', txt[i:], re.IGNORECASE)
                    next_close = pat_div_close.search(txt[i:])
                    if not next_close:
                        break
                    pos_close = i + next_close.start()
                    pos_open = i + next_open.start() if next_open else -1
                    if next_open and pos_open < pos_close:
                        depth += 1
                        i = pos_open + 5
                    else:
                        depth -= 1
                        i = pos_close + 8
                        if depth == 0:
                            div_end = i

                if div_end is None:
                    continue

                inner_content = txt[m_start.end(): div_end - 8]

                coll_m = pat_coll.match(txt, div_end)
                if coll_m:
                    coll_content_raw = coll_m.group(3)
                    block_end = coll_m.end()
                else:
                    coll_content_raw = '文字'
                    block_end = div_end

                id_dm = re.search(r'\*\s*default:\s*<([^>]+)>', inner_content)
                id_val = id_dm.group(1).strip() if id_dm else '你的ID'

                parsed_coll = parse_wikidot_to_editor_html(coll_content_raw.strip(), theme_type)

                ll_html = (
                    '<div class="scp-component login-logout-box" data-type="login-logout"'
                    ' contenteditable="false"'
                    ' style="border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;">'
                    '<table class="login-form-table" contenteditable="false"'
                    ' style="margin:0.5em auto; border-collapse:collapse;">'
                    '<tr>'
                    '<td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">ID</td>'
                    '<td>'
                    f'<span class="login-id-value" contenteditable="true"'
                    f' style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;">'
                    f'{id_val}</span>'
                    '</td>'
                    '</tr>'
                    '<tr>'
                    '<td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">\u5bc6\u7801</td>'
                    '<td>'
                    '<span contenteditable="false"'
                    ' style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px;'
                    ' font-family:sans-serif; color:#555; letter-spacing:2px;">'
                    '\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb</span>'
                    '</td>'
                    '</tr>'
                    '<tr>'
                    '<td contenteditable="false"></td>'
                    '<td style="text-align:center;" contenteditable="false">'
                    '<button contenteditable="false"'
                    ' style="padding:2px 18px; border:1px solid #aaa; background:#f4f4f4;  font-family:sans-serif;">'
                    '\u767b\u5165</button>'
                    '</td>'
                    '</tr>'
                    '</table>'
                    '<hr contenteditable="false" style="border:none; border-top:1px solid #ccc; margin:6px 0;">'
                    '<div contenteditable="false"'
                    ' style="font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;">'
                    '[\u767b\u5165]\u2194[\u767b\u51fa] \u6298\u53e0\u5185\u5bb9</div>'
                    '<div class="login-collapsible-content" contenteditable="true"'
                    ' style="min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;">'
                    f'{parsed_coll}'
                    '</div>'
                    '</div>'
                )
                result.append(txt[cursor:div_start])
                result.append(register_ph(ll_html))
                cursor = block_end

            result.append(txt[cursor:])
            return ''.join(result)

        text = process_fakeprot_source(text)

    def wikidot_table_replacer(txt):
        result = []
        cursor = 0
        pat_tbl_start = re.compile(r'\[\[table(\s[^\]]*)?\]\]', re.IGNORECASE)
        pat_tbl_end = re.compile(r'\[\[/table\]\]', re.IGNORECASE)
        pat_row = re.compile(r'\[\[row(\s[^\]]*)?\]\]', re.IGNORECASE)
        pat_row_end = re.compile(r'\[\[/row\]\]', re.IGNORECASE)
        pat_cell = re.compile(r'\[\[cell(\s[^\]]*)?\]\]', re.IGNORECASE)
        pat_cell_end = re.compile(r'\[\[/cell\]\]', re.IGNORECASE)

        for m_tbl in pat_tbl_start.finditer(txt):
            tbl_start = m_tbl.start()
            if tbl_start < cursor: continue
            m_tend = pat_tbl_end.search(txt, m_tbl.end())
            if not m_tend: continue
            tbl_end = m_tend.end()

            tbl_params = (m_tbl.group(1) or '').strip()
            inner_txt = txt[m_tbl.end(): m_tend.start()]

            rows_html = ''
            row_cursor = 0
            for m_row in pat_row.finditer(inner_txt):
                if m_row.start() < row_cursor: continue
                m_rend = pat_row_end.search(inner_txt, m_row.end())
                if not m_rend: continue

                row_params = (m_row.group(1) or '').strip()
                row_inner = inner_txt[m_row.end(): m_rend.start()]

                row_style_m = re.search(r'style=["\']([^"\']*)["\']', row_params, re.IGNORECASE)
                row_style = row_style_m.group(1) if row_style_m else ''
                row_style_attr = f' style="{row_style}"' if row_style else ''
                row_data = f' data-wd-style="{row_style}"' if row_style else ''

                cells_html = ''
                cell_cursor = 0
                for m_cell in pat_cell.finditer(row_inner):
                    if m_cell.start() < cell_cursor: continue
                    m_cend = pat_cell_end.search(row_inner, m_cell.end())
                    if not m_cend: continue

                    cell_params = (m_cell.group(1) or '').strip()
                    cell_inner_raw = row_inner[m_cell.end(): m_cend.start()].strip()

                    cell_style_m = re.search(r'style=["\']([^"\']*)["\']', cell_params, re.IGNORECASE)
                    cell_style = cell_style_m.group(1) if cell_style_m else ''
                    cell_style_attr = f' style="{cell_style}"' if cell_style else ''
                    cell_data = f' data-wd-style="{cell_style}"' if cell_style else ''

                    parsed_cell = parse_wikidot_to_editor_html(cell_inner_raw, theme_type)
                    cells_html += f'<td{cell_style_attr}{cell_data} contenteditable="true">{parsed_cell}</td>'
                    cell_cursor = m_cend.end()

                rows_html += f'<tr{row_style_attr}{row_data}>{cells_html}</tr>'
                row_cursor = m_rend.end()

            tbl_style_m = re.search(r'style=["\']([^"\']*)["\']', tbl_params, re.IGNORECASE)
            tbl_style = tbl_style_m.group(1) if tbl_style_m else ''
            tbl_style_attr = f' style="{tbl_style}"' if tbl_style else ''
            tbl_data = f' data-wd-style="{tbl_style}"' if tbl_style else ''

            tbl_html = (
                f'<table class="scp-component wikidot-adv-table" data-type="wikidot-table"'
                f'{tbl_style_attr}{tbl_data} contenteditable="false">'
                f'<tbody>{rows_html}</tbody></table>'
            )
            result.append(txt[cursor: tbl_start])
            result.append(register_ph(tbl_html))
            cursor = tbl_end

        result.append(txt[cursor:])
        return ''.join(result)

    text = wikidot_table_replacer(text)

    def collapsible_replacer(match):
        show_t = match.group(1) or "+ Open"
        hide_t = match.group(2) or "- Close"
        content = match.group(3)
        parsed_inner = parse_wikidot_to_editor_html(content, theme_type)
        html = f'''<div class="scp-component collapsible-box open" data-type="collapsible" contenteditable="false"><div class="collapsible-header"><span><span class="title-label">显示标题:</span> <span class="title-input" data-field="show" contenteditable="true">{show_t}</span></span><span><span class="title-label">隐藏标题:</span> <span class="title-input" data-field="hide" contenteditable="true">{hide_t}</span></span></div><div class="collapsible-content-area" contenteditable="true">{parsed_inner}</div></div>'''
        return register_ph(html)

    def process_nested_divs(text):
        output = []
        cursor = 0
        while True:
            start_idx = text.find('[[div', cursor)
            if start_idx == -1:
                output.append(text[cursor:])
                break
            
            output.append(text[cursor:start_idx])
            content_start_idx = text.find(']]', start_idx)
            if content_start_idx == -1:
                output.append(text[start_idx:])
                break
            
            params = text[start_idx+5 : content_start_idx].strip()
            content_start_idx += 2 
            
            nesting = 1
            current = content_start_idx
            found_end = False
            
            while True:
                next_open = text.find('[[div', current)
                next_close = text.find('[[/div]]', current)
                
                if next_close == -1: break
                if next_open != -1 and next_open < next_close:
                    nesting += 1
                    current = next_open + 5
                else:
                    nesting -= 1
                    current = next_close + 8 
                    if nesting == 0:
                        found_end = True
                        break
                        
            if found_end:
                content = text[content_start_idx : next_close]
                replaced_html = div_replacer(None, params, content)
                output.append(replaced_html)
                cursor = next_close + 8
            else:
                output.append(text[start_idx:])
                break
        return "".join(output)

    _PAGE_CSS_SIG = 'linear-gradient(to top ,rgb(202, 219, 228) 0%, rgb(231, 233, 220) 8%)'
    _has_page_css = [_PAGE_CSS_SIG in text]
    _PAGE_NOTE_STYLE = (
        'display:block; overflow:hidden; '
        "font-family:'Monotype Corsiva','Bradley Hand ITC',sans-serif; "
        'background-attachment:scroll; '
        'background-image:linear-gradient(to top,rgb(202,219,228) 0%,rgb(231,233,220) 8%); '
        'background-position:0px 8px; background-repeat:repeat; background-size:100% 20px; '
        'border:1px solid #CCC; border-radius:10px; padding:10px; margin-bottom:10px; '
        'box-shadow:0px 1px 3px rgba(0,0,0,0.2); position:relative; clear:both;'
    )

    _FAKEPROT_CSS_SIG = '.fakeprot .mailform-box .buttons'
    _has_fakeprot_css = [_FAKEPROT_CSS_SIG in text] 

    def extract_top_div(txt, start_pos):
        tag_end = txt.find(']]', start_pos)
        if tag_end == -1: return None
        params_str = txt[start_pos + 5 : tag_end].strip() 
        depth = 1
        i = tag_end + 2
        while i < len(txt) and depth > 0:
            next_open = txt.find('[[div', i)
            next_close = txt.find('[[/div]]', i)
            if next_close == -1: break
            if next_open != -1 and next_open < next_close:
                depth += 1; i = next_open + 5
            else:
                depth -= 1
                if depth == 0:
                    inner = txt[tag_end + 2 : next_close]
                    return (params_str, inner, next_close + 8)
                i = next_close + 8
        return None

    def div_replacer(match=None, params_arg=None, content_arg=None):
        if match:
            start_pos = match.start()
            info = extract_top_div(text, start_pos)
            if info:
                params, content, end_pos = info
            else:
                params = match.group(1).strip()
                content = match.group(2)
                end_pos = start_pos + len(match.group(0))
        else:
            params = params_arg
            content = content_arg
            start_pos = -1 
            end_pos = -1

        if 'class="terminal"' in params or "class='terminal'" in params:
             def extract_div_content(src, cls_marker):
                 pat1 = f'[[div class="{cls_marker}"]]'
                 pat2 = f"[[div class='{cls_marker}']]"
                 start = src.find(pat1)
                 quote_len = len(pat1)
                 if start == -1:
                     start = src.find(pat2)
                     quote_len = len(pat2)
                 if start == -1: return None
                 body_start = start + quote_len
                 depth = 1
                 i = body_start
                 while i < len(src) and depth > 0:
                     next_open = src.find('[[div', i)
                     next_close = src.find('[[/div]]', i)
                     if next_close == -1: break
                     if next_open != -1 and next_open < next_close:
                         depth += 1
                         i = next_open + 5
                     else:
                         depth -= 1
                         if depth == 0: return src[body_start:next_close]
                         i = next_close + 8
                 return None

             text_content = extract_div_content(content, 'text')

             if text_content is not None:
                 def fix_hr_lines(txt):
                     lines = txt.split('\n')
                     out = []
                     for ln in lines:
                         if re.match(r'^-{4,}\s*$', ln):
                             count = len(ln.rstrip())
                             out.append('@' + '-' * count + '@')
                         else: out.append(ln)
                     return '\n'.join(out)
                 text_content = fix_hr_lines(text_content.strip())
                 parsed_text = parse_wikidot_to_editor_html(text_content, theme_type)

                 html = f'''<div class="scp-component div-box terminal" data-type="div-block" contenteditable="false">
                 <div class="div-header" onclick="toggleDiv(this)" style="" title="点击折叠/展开">DIV: class="terminal"</div>
                 <div class="div-content" contenteditable="true">
                    <div class="scp-component div-box scanline" data-type="div-block" contenteditable="false">
                        <div class="div-header" onclick="toggleDiv(this)" style="" title="点击折叠/展开">DIV: class="scanline"</div>
                        <div class="div-content" contenteditable="true"></div>
                    </div>
                    <div class="scp-component div-box text" data-type="div-block" contenteditable="false">
                        <div class="div-header" onclick="toggleDiv(this)" style="" title="点击折叠/展开">DIV: class="text"</div>
                        <div class="div-content" contenteditable="true">{parsed_text}</div>
                    </div>
                 </div>
                 </div>'''
                 return register_ph(html)

        parsed_inner = parse_wikidot_to_editor_html(content, theme_type)
        if "border: 1px solid #FFC107" in params or "border: 1px solid rgb(255, 193, 7)" in params:
             html = f'''<div class="scp-component raisa-box" data-type="raisa-notice" contenteditable="false"><div class="raisa-header" contenteditable="false">NOTICE FROM THE RECORDS AND INFORMATION SECURITY ADMINISTRATION</div><div class="raisa-content" contenteditable="true">{parsed_inner}</div><div class="raisa-footer" contenteditable="false"></div></div>'''
             return register_ph(html)

        if "scp_trans.png" in params and ("border: solid 2px black" in params or "border: 2px solid black" in params):
             html = f'''<div class="scp-component class-warning-box" data-type="class-warning" contenteditable="false"><div class="class-warning-content" contenteditable="true"><div class="class-warning-inner">{parsed_inner}</div></div></div>'''
             return register_ph(html)

        if "kaktuskontainer" in params and "width: 600px" in params:
             html = f'''<div class="scp-component o5-box" data-type="o5-command" contenteditable="false"><div class="o5-content" contenteditable="true">{parsed_inner}</div></div>'''
             return register_ph(html)

        if _has_page_css[0] and ('class="page"' in params or "class='page'" in params):
            html = (f'<div class="scp-component page-note-box" data-type="page-note" '
                    f'contenteditable="false" style="{_PAGE_NOTE_STYLE}">'
                    f'<div class="page-note-label" contenteditable="false" '
                    f'style="font-size:10px;color:#aaa;text-align:right;margin-bottom:2px;">便签纸</div>'
                    f'<div class="page-note-content" contenteditable="true" '
                    f'style="font-family:\'Monotype Corsiva\',\'Bradley Hand ITC\',sans-serif;line-height:20px;">'
                    f'{parsed_inner}</div></div>')
            return register_ph(html)

        use_basalt = (theme_type == "basalt") or _has_basalt_in_source
        
        if use_basalt:
            class_match = re.search(r'class=["\']([^"\']+)["\']', params)
            classes = class_match.group(1).split() if class_match else []

            if "floatbox" in classes:
                right_cls = " right" if "right" in classes else ""
                html = f'''<div class="scp-component div-box basalt-div basalt-floatbox-box{right_cls}" data-type="div-block" contenteditable="false">
                    <div class="div-header" contenteditable="false" onclick="toggleDiv(this)" title="点击折叠/展开">[[div class="{" ".join(classes)}"]]</div>
                    <div class="div-content" contenteditable="true">{parsed_inner}</div>
                </div>'''
                return register_ph(html)

            basalt_special_map = {
                "blockquote": "basalt-blockquote-box",
                "notation": "basalt-notation-box",
                "jotting": "basalt-jotting-box",
                "modal": "basalt-modal-box",
                "smallmodal": "basalt-smallmodal-box",
                "papernote": "basalt-papernote-box",
                "document": "basalt-document-box",
                "darkdocument": "basalt-darkdocument-box",
                "raisa_memo": "basalt-raisa_memo-box",
                "classification_memo": "basalt-classification_memo-box",
                "ettra_memo": "basalt-ettra_memo-box",
                "ethics_memo": "basalt-ethics_memo-box",
                "temporal_memo": "basalt-temporal_memo-box",
                "overwatch_memo": "basalt-overwatch_memo-box",
                "miscomm_memo": "basalt-miscomm_memo-box"
            }
            for cls, box_cls in basalt_special_map.items():
                if cls in classes:
                    box_classes = ["scp-component", "div-box", "basalt-div", box_cls]
                    if cls in ["document", "darkdocument"]:
                        box_classes.append("basalt-doc-wrapper")
                        box_classes.append("full-width")
                    if cls.endswith("_memo"):
                        box_classes.append("basalt-memo-box")
                        
                    box_cls_str = " ".join(box_classes)
                    html = f'''<div class="{box_cls_str}" data-type="div-block" contenteditable="false">
                        <div class="div-header" contenteditable="false" onclick="toggleDiv(this)" title="点击折叠/展开">[[div class="{" ".join(classes)}"]]</div>
                        <div class="div-content" contenteditable="true">{parsed_inner}</div>
                    </div>'''
                    return register_ph(html)

        html = f'''<div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true" onclick="toggleDiv(this)" style="" title="点击折叠/展开">DIV: {params}</div><div class="div-content" contenteditable="true">{parsed_inner}</div></div>'''
        return register_ph(html)

    def pre_detect_components(txt):
        result = []
        cursor = 0
        while True:
            pos = txt.find('[[div', cursor)
            if pos == -1:
                result.append(txt[cursor:])
                break
            info = extract_top_div(txt, pos)
            if info is None:
                result.append(txt[cursor:])
                break
            params_str, inner_content, end_pos = info
            matched = False

            if 'FFC107' in params_str or 'rgb(255, 193, 7)' in params_str:
                result.append(txt[cursor:pos])
                parsed_inner = parse_wikidot_to_editor_html(inner_content, theme_type)
                raisa_style = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5; position: relative; clear: both;"
                html = (f'<div class="scp-component raisa-box" data-type="raisa-notice" contenteditable="false" style="{raisa_style}">'
                        f'<div class="raisa-header" contenteditable="false" style="text-align:center; font-weight:bold; border-bottom:1px solid #FFC107; margin-bottom:8px; padding-bottom:4px;">NOTICE FROM THE RECORDS AND INFORMATION SECURITY ADMINISTRATION</div>'
                        f'<div class="raisa-content" contenteditable="true" style="text-align:center;">{parsed_inner}</div>'
                        f'<div class="raisa-footer" contenteditable="false"></div></div>')
                result.append(register_ph(html))
                cursor = end_pos; matched = True

            elif 'kaktuskontainer' in params_str and '600px' in params_str:
                result.append(txt[cursor:pos])
                m1 = re.search(r'\+\+\*\s*(.*?)(?=\n|$)', inner_content)
                part1_wiki = m1.group(1).strip() if m1 else "##black|根据监督者议会的命令##"
                m2 = re.search(r'\+\+\*.*?\n(.*?)(?=\[\[/=\]\])', inner_content, re.DOTALL)
                part2_wiki = m2.group(1).strip() if m2 else "##black|以下文件为X/XXXX级机密。禁止未经授权的访问。##"
                m3 = re.search(r'^\s*=\s*(.*?)(?=\n|$)', inner_content, re.MULTILINE)
                part3_wiki = m3.group(1).strip() if m3 else "**##black|XXXX##**"
                
                p1_html = parse_wikidot_to_editor_html(part1_wiki, theme_type).strip()
                p2_html = parse_wikidot_to_editor_html(part2_wiki, theme_type).strip()
                p3_html = parse_wikidot_to_editor_html(part3_wiki, theme_type).strip()
                
                def strip_p(h):
                    if h.startswith('<p>') and h.endswith('</p>'): return h[3:-4]
                    return h
                p1_html = strip_p(p1_html)
                p2_html = strip_p(p2_html)
                p3_html = strip_p(p3_html)
                
                o5_style = "background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px; position: relative; clear: both;"
                html = (f'<div class="scp-component o5-box" data-type="o5-command" contenteditable="false" style="{o5_style}">'
                        f'<div class="o5-content" contenteditable="true" style="padding-top:80px; padding-bottom:40px;">'
                        f'<div class="o5-center-block" style="text-align:center;">'
                        f'<h2 class="o5-h2" style="margin:0;">{p1_html}</h2>'
                        f'<div class="o5-p">{p2_html}</div>'
                        f'</div>'
                        f'<h1 class="o5-h1" style="text-align:center;">{p3_html}</h1>'
                        f'</div></div>')
                result.append(register_ph(html))
                cursor = end_pos; matched = True

            elif 'the-great-hippo' in params_str and 'solid 2px black' in params_str:
                pre_text = txt[cursor:pos]
                post_text = txt[end_pos:]
                has_pre_eq = pre_text.rstrip().endswith('[[=]]')
                has_post_eq = post_text.lstrip().startswith('[[/=]]')
                
                if has_pre_eq:
                    eq_idx = pre_text.rfind('[[=]]')
                    result.append(pre_text[:eq_idx])
                else:
                    result.append(pre_text)
                    
                parsed_inner = parse_wikidot_to_editor_html(inner_content, theme_type)
                if '</span><span style="font-size:larger' in parsed_inner:
                    parsed_inner = parsed_inner.replace('</span><span style="font-size:larger', '</span><hr class="class-warning-hr" style="border:none; border-top:1px solid #777; margin:10px 0;"><span style="font-size:larger')
                
                cw_style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) center no-repeat; border: solid 2px #000; padding: 1px 15px; box-shadow: 0 1px 3px rgba(0,0,0,.2); margin: 10px auto; width: fit-content; text-align: center; position: relative; clear: both;"
                html = (f'<div class="scp-component class-warning-box" data-type="class-warning" contenteditable="false" style="{cw_style}">'
                        f'<div class="class-warning-content" contenteditable="true">'
                        f'<div class="class-warning-inner" style="text-align:center;">{parsed_inner}</div>'
                        f'</div></div>')
                result.append(register_ph(html))
                
                cursor = end_pos
                if has_post_eq:
                    spaces = len(post_text) - len(post_text.lstrip())
                    cursor += spaces + 6
                matched = True

            elif 'email-example' in params_str:
                result.append(txt[cursor:pos])
                m_col = re.search(r'\[\[collapsible\s+show="(.*?)"\s+hide="(.*?)"\]\]', inner_content, re.IGNORECASE)
                show_title = m_col.group(1) if m_col else "{show_title}"
                hide_title = m_col.group(2) if m_col else "{hide_title}"

                raw_block_text = txt[pos:end_pos]
                to_list = re.findall(r'\*\*\s*至\s*[：:]\s*(?:\*\*)?\s*(.*?)(?=\r?\n|$)', raw_block_text)
                from_list = re.findall(r'\*\*\s*自\s*[：:]\s*(?:\*\*)?\s*(.*?)(?=\r?\n|$)', raw_block_text)
                subj_list = re.findall(r'\*\*\s*主题\s*[：:]\s*(?:\*\*)?\s*(.*?)(?=\r?\n|$)', raw_block_text)
                body_list_raw = re.findall(r'\*\*\s*主题\s*[：:].*?\[\[/div\]\]\s*-{3,}\s*\r?\n(.*?)(?=\s*\[\[/div\]\])', raw_block_text, re.DOTALL | re.IGNORECASE)

                emails = []
                for i in range(2):
                    to_text = to_list[i].strip() if i < len(to_list) and to_list[i].strip() else f"{{to{i+1}}}"
                    from_text = from_list[i].strip() if i < len(from_list) and from_list[i].strip() else f"{{from{i+1}}}"
                    subj_text = subj_list[i].strip() if i < len(subj_list) and subj_list[i].strip() else f"{{subj{i+1}}}"
                    cont_raw = body_list_raw[i].strip() if i < len(body_list_raw) and body_list_raw[i].strip() else f"{{cont{i+1}}}"
                    
                    to_text = re.sub(r'^\*+|\*+$', '', to_text).strip()
                    from_text = re.sub(r'^\*+|\*+$', '', from_text).strip()
                    subj_text = re.sub(r'^\*+|\*+$', '', subj_text).strip()
                    
                    cont_text = parse_wikidot_to_editor_html(cont_raw, theme_type) if cont_raw != f"{{cont{i+1}}}" else cont_raw
                    emails.append((to_text, from_text, subj_text, cont_text))
                
                to1, from1, subj1, cont1 = emails[0]
                to2, from2, subj2, cont2 = emails[1]

                html = f'''
    <div class="scp-component email-example-box" data-type="email-example" contenteditable="false" style="border: 2px dashed #ccc; padding: 10px; margin: 20px 0; background: #fdfdfd;">
        <div style="border-bottom: 1px solid #999; margin-bottom: 10px; text-align: left;">
            <span class="email-show-title" contenteditable="true" style="color:#b01; font-weight:bold; ">{show_title}</span>
            <span style="color:#888; margin-left:10px; font-size: 12px;">(展开标题 - 点击编辑)</span>
            <br>
            <span class="email-hide-title" contenteditable="true" style="color:#b01; font-weight:bold; ">{hide_title}</span>
            <span style="color:#888; margin-left:10px; font-size: 12px;">(折叠标题 - 点击编辑)</span>
        </div>
        <div class="email-item" style="border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px auto; box-shadow: 0 1px 3px rgba(0,0,0,.5); text-align: left; background: #fff;">
            <div class="tofrom" style="margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon; text-align: left;">
                <b>至：</b><span class="email-to1" contenteditable="true">{to1}</span><br>
                <b>自：</b><span class="email-from1" contenteditable="true">{from1}</span><br>
                <b>主题：</b><span class="email-subj1" contenteditable="true">{subj1}</span>
            </div>
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 10px 0;">
            <div class="email-content1" contenteditable="true" style="min-height: 30px;">{cont1}</div>
        </div>
        <div style="text-align: center; color: #888; margin: 10px 0;">@@ @@</div>
        <div class="email-item" style="border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px auto; box-shadow: 0 1px 3px rgba(0,0,0,.5); text-align: left; background: #fff;">
            <div class="tofrom" style="margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon; text-align: left;">
                <b>至：</b><span class="email-to2" contenteditable="true">{to2}</span><br>
                <b>自：</b><span class="email-from2" contenteditable="true">{from2}</span><br>
                <b>主题：</b><span class="email-subj2" contenteditable="true">{subj2}</span>
            </div>
            <hr style="border: 0; border-top: 1px solid #ccc; margin: 10px 0;">
            <div class="email-content2" contenteditable="true" style="min-height: 30px;">{cont2}</div>
        </div>
        <div class="email-css-indicator" contenteditable="false" style="background-color:#f0f0f0;border:1px solid #ccc;padding:5px;margin-top:10px;font-size:12px;color:#666;font-family:monospace;text-align:left;"><i>[CSS模块已折叠连体，导出时将自动附带相应的格式代码及水平线居中排列]</i></div>
    </div>
'''
                result.append(register_ph(html))
                cursor = end_pos; matched = True

            elif 'class="orderwrapper"' in params_str or "class='orderwrapper'" in params_str:
                result.append(txt[cursor:pos])
                m_title = re.search(r'\[\[div class="ordertitle"\]\]\s*\+\*\s*(.*?)\s*\[\[/div\]\]', inner_content, re.DOTALL)
                title_text = m_title.group(1).strip() if m_title else "标题"
                
                m_desc = re.search(r'\[\[div class="orderdescription"\]\]\s*_\s*\+\*\s*(.*?)\n(.*?)\[\[/div\]\]', inner_content, re.DOTALL)
                desc_h1_text = m_desc.group(1).strip() if m_desc else "副标题"
                desc_p_text = m_desc.group(2).strip() if m_desc else "描述"
                
                m_item = re.search(r'\[\[div class="itemno"\]\]\s*\+\*\s*(.*?)\s*\[\[/div\]\]', inner_content, re.DOTALL)
                item_text = m_item.group(1).strip() if m_item else "XXXX"
                
                title_html = parse_wikidot_to_editor_html(title_text, theme_type).strip()
                desc_h1_html = parse_wikidot_to_editor_html(desc_h1_text, theme_type).strip()
                desc_p_html = parse_wikidot_to_editor_html(desc_p_text, theme_type).strip()
                item_html = parse_wikidot_to_editor_html(item_text, theme_type).strip()
                
                def strip_p(h):
                    if h.startswith('<p>') and h.endswith('</p>'): return h[3:-4]
                    return h
                    
                title_html = strip_p(title_html)
                desc_h1_html = strip_p(desc_h1_html)
                desc_p_html = strip_p(desc_p_html)
                item_html = strip_p(item_html)
                
                box_style = "position:relative;width:auto;text-align:center;clear:both;min-height:300px;margin:20px 0;"
                bg_style = "position:absolute;top:0;bottom:0;left:0;right:0;width:295px;height:295px;margin:auto;background-image:url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png);background-size:295px 295px;background-repeat:no-repeat;background-position:center;z-index:0;opacity:0.3;"
                
                html = (f'<div class="scp-component foundation-bg-box" data-type="foundation-bg" contenteditable="false" style="{box_style}">'
                        f'<div style="{bg_style}"></div>'
                        f'<div style="position:relative;z-index:1;width:100%;height:295px;">'
                        f'<div class="foundation-title" style="position:absolute;left:0;right:0;top:38px;" contenteditable="true">'
                        f'<h1 style="font-size:220%;color:#555;margin:0;">{title_html}</h1></div>'
                        f'<div class="foundation-desc" style="position:absolute;left:0;right:0;top:85px;width:100%;" contenteditable="true">'
                        f'<h1 style="font-size:120%;color:#555;margin:0;">{desc_h1_html}</h1>'
                        f'<p style="font-size:90%;color:#555;margin:0;">{desc_p_html}</p></div>'
                        f'<div class="foundation-itemno" style="position:absolute;left:0;right:0;bottom:27px;" contenteditable="true">'
                        f'<h1 style="font-size:170%;color:#555;margin:0;">{item_html}</h1></div>'
                        f'</div>'
                        f'<div class="foundation-css-indicator" contenteditable="false" style="background-color:#f0f0f0;border:1px solid #ccc;padding:5px;margin-top:10px;font-size:12px;color:#666;font-family:monospace;text-align:left;"><i>[CSS模块已折叠连体，导出时将自动附带相应的格式代码]</i></div>'
                        f'</div>')
                result.append(register_ph(html))
                cursor = end_pos; matched = True

            if not matched:
                result.append(txt[cursor:pos + 5])
                cursor = pos + 5

        return ''.join(result)

    text = pre_detect_components(text)
    
    text = re.sub(r'\[\[collapsible show="([^"]*)" hide="([^"]*)"\]\](.*?)\[\[/collapsible\]\]', collapsible_replacer, text, flags=re.DOTALL)
    
    text = process_nested_divs(text)

    def css_replacer(match):
        content = match.group(1).strip()
        PAGE_CSS_SIG = 'linear-gradient(to top ,rgb(202, 219, 228) 0%, rgb(231, 233, 220) 8%)'
        if PAGE_CSS_SIG in content: return ''  
        if '.fakeprot .mailform-box .buttons' in content: return ''  
        if '.orderwrapper {position: relative;width: auto;text-align: center;}.council1' in content: return ''  
        if '.email-example .collapsible-block-folded a.collapsible-block-link' in content and 'animation: blink 0.8s' in content: return ''

        is_terminal = ".danke" in content and ".agent" in content
        if is_terminal:
            html = f'''<div class="scp-component css-box" data-type="css-module" contenteditable="false">
            <details>
                <summary class="css-header" style=" user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary>
                <div class="css-content" contenteditable="true">{content}</div>
            </details>
            <div class="css-hint">被css影响的代码紧跟css模块下面</div></div>'''
        else:
            html = f'''<div class="scp-component css-box" data-type="css-module" contenteditable="false"><div class="css-header" onclick="toggleCss(this)" style="" title="点击折叠/展开">CSS Module (Valid CSS Only) (点击折叠)</div><div class="css-content" contenteditable="true">{content}</div><div class="css-hint">被css影响的代码紧跟css模块下面</div></div>'''
        return register_ph(html)

    text = re.sub(r'\[\[module CSS\]\](.*?)\[\[/module\]\]', css_replacer, text, flags=re.DOTALL|re.IGNORECASE)

    def user_replacer(match):
        html = f'<span class="scp-component user-tag" data-type="user" contenteditable="false"><div class="user-icon"></div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{match.group(1)}</span></span>'
        return register_ph(html)
    text = re.sub(r'\[\[user ([^\]]+)\]\]', user_replacer, text)
    
    def user_adv_replacer(match):
        html = f'<span class="scp-component user-tag" data-type="user-adv" contenteditable="false"><div class="user-icon" style="background:gold; text-align:center; line-height:12px; font-size:10px; color:#fff;">★</div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{match.group(1)}</span></span>'
        return register_ph(html)
    text = re.sub(r'\[\[\*user ([^\]]+)\]\]', user_adv_replacer, text)

    def toc_replacer(match):
         html = '<div class="scp-component" data-type="toc" contenteditable="false" style="border: 1px dashed #999; padding: 5px; background: #f0f0f0;"><b>目录 (TOC)</b><br>[[toc]]</div>'
         return register_ph(html)
    text = re.sub(r'\[\[toc\]\]', toc_replacer, text)

    def audio_replacer(match):
        audio_url = match.group(1).strip()
        html = f'''<div class="scp-component html5player-box" data-type="html5player" contenteditable="false" style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; background: #f9f9f9; width: 100%; box-sizing: border-box; display: flex; align-items: center; gap: 10px;">
            <audio controls preload="metadata" style="height: 30px; flex-grow: 1;">
                <source src="{audio_url}" type="audio/mpeg">
                <source src="{audio_url}" type="audio/ogg">
                <source src="{audio_url}" type="audio/wav">
            </audio>
            <a href="edit-audio-link://new" onclick="window._currentAudioLink=this;" style="color: #b01; font-weight: bold; cursor: pointer; text-decoration: underline; white-space: nowrap;">链接</a>
            <span class="html5player-url" style="display: none;">{audio_url}</span>
        </div>'''
        return register_ph(html)
    text = re.sub(r'\[\[include\s+:snippets:html5player\s*\|type=audio\s*\|url=(.*?)\]\]', audio_replacer, text, flags=re.IGNORECASE)

    def fn_replacer(match):
        content = match.group(1)
        html = f'<span class="scp-component scp-footnote" data-type="footnote" data-content="{content}" title="{content}" contenteditable="false">#</span>'
        return register_ph(html)
    text = re.sub(r'\[\[footnote\]\](.*?)\[\[/footnote\]\]', fn_replacer, text, flags=re.DOTALL)

    def bf_replacer(match):
        content = match.group(2).strip()
        html = (f'<span class="scp-component scp-footnote" data-type="footnote"'
                f' data-content="{content}" title="{content}" contenteditable="false">#</span>')
        return register_ph(html)
    text = re.sub(
        r'\[\[span\s+class=["\']fnnum["\']\]\](.*?)\[\[/span\]\]'
        r'\[\[span\s+class=["\']fncon["\']\]\](.*?)\[\[/span\]\]',
        bf_replacer, text, flags=re.DOTALL)

    text = re.sub(r'\[\[\s*size\s+([^\]]+)\]\]', r'<span style="font-size:\1">', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[\s*/size\s*\]\]', r'</span>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\[\s*<\s*\]\]', r'<div style="text-align: left;">', text)
    text = re.sub(r'\[\[\s*/<\s*\]\]', r'</div>', text)
    text = re.sub(r'\[\[\s*>\s*\]\]', r'<div style="text-align: right;">', text)
    text = re.sub(r'\[\[\s*/>\s*\]\]', r'</div>', text)
    text = re.sub(r'\[\[\s*==\s*\]\]', r'<div style="text-align: justify;">', text)
    text = re.sub(r'\[\[\s*/==\s*\]\]', r'</div>', text)
    text = re.sub(r'\[\[\s*=\s*\]\]', r'<div style="text-align: center;">', text)
    text = re.sub(r'\[\[\s*/=\s*\]\]', r'</div>', text)
    text = re.sub(r'##([^\|\n]+)\|((?:(?!##).|\n)*)##', lambda m: f'<span style="color: {m.group(1).strip()}">{m.group(2)}</span>', text)

    lines = text.split('\n')
    final_lines = []
    buffer_table = []
    buffer_quote = []
    list_stack = [] 
    
    def flush_table():
        if not buffer_table: return
        t_html = '<table border="1" class="wikidot-table">'
        for row in buffer_table:
            cells = [c for c in row.split('||') if c]
            t_html += "<tr>"
            for c in cells:
                tag = "td"
                c_text = c
                if c.startswith('~'):
                    tag = "th"
                    c_text = c[1:]
                t_html += f'<{tag} contenteditable="true">{c_text.strip()}</{tag}>'
            t_html += "</tr>"
        t_html += "</table>"
        final_lines.append(register_ph(t_html))
        buffer_table.clear()

    def flush_quote():
        if not buffer_quote: return
        content = "<br>".join(buffer_quote)
        final_lines.append(f'<blockquote>{content}</blockquote>')
        buffer_quote.clear()

    def flush_list():
        while list_stack:
            _, tag = list_stack.pop()
            final_lines.append(f'</{tag}>')

    list_buffer_empty = []
    for line_raw in lines:
        line = line_raw.rstrip('\r\n')
        list_match = re.match(r'^([\*#]+)\s+(.*)$', line)
        if list_match:
            flush_table()
            flush_quote()
            markers, content = list_match.groups()
            depth = len(markers)
            tag = 'ul' if markers[-1] == '*' else 'ol'
            is_continuation = False
            if list_stack and list_stack[-1][0] == depth and list_stack[-1][1] == tag:
                is_continuation = True
            if is_continuation and list_buffer_empty:
                if final_lines and final_lines[-1].endswith('</li>'):
                    last_li = final_lines.pop()
                    final_lines.append(last_li[:-5] + '<br>' * len(list_buffer_empty) + '</li>')
                list_buffer_empty.clear()
            if not is_continuation:
                while list_stack and (list_stack[-1][0] > depth or (list_stack[-1][0] == depth and list_stack[-1][1] != tag)):
                    _, old_tag = list_stack.pop()
                    final_lines.append(f'</{old_tag}>')
                if not list_stack or list_stack[-1][0] < depth:
                    list_stack.append((depth, tag))
                    final_lines.append(f'<{tag}>')
            final_lines.append(f'<li>{content.strip()}</li>')
            continue

        if line.startswith('||') and line.endswith('||') and '_WIKIDOT_PH_' not in line:
            flush_list()
            list_buffer_empty.clear()
            flush_quote()
            buffer_table.append(line)
        elif line.startswith('>'):
            flush_list()
            list_buffer_empty.clear()
            flush_table()
            q_line = line[1:]
            if q_line.startswith(' '): q_line = q_line[1:]
            buffer_quote.append(q_line)
        elif list_stack and not line.strip():
            list_buffer_empty.append(line)
            continue
        else:
            flush_list()
            list_buffer_empty.clear()
            flush_table()
            flush_quote()
            final_lines.append(line)

    flush_list()
    flush_table()
    flush_quote()
    text = "\n".join(final_lines)

    def dash_protector(m):
        count = len(m.group(1))
        visual = '&#45;' * count
        return f'<span class="custom-dash" data-count="{count}">{visual}</span>'
    text = re.sub(r'@(-{3,})@', dash_protector, text)

    text = re.sub(r'^(\+{1,6})\s+(.*)$', lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>', text, flags=re.MULTILINE)
    
    def hr_replacer(m): return register_ph('<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>')
    text = re.sub(r'^-{4,}\s*$', hr_replacer, text, flags=re.MULTILINE)
    
    def triple_link_replacer(match):
        url = match.group(1).strip()
        text_content = match.group(2).strip()
        target = ""
        if url.startswith('*'):
            url = url[1:].strip()
            target = ' target="_blank"'
        return f'<a href="{url}"{target}>{text_content}</a>'
    
    text = re.sub(r'\[\[\[(\*?[^\|\]]+)\|\s*(.*?)\]\]\]', triple_link_replacer, text)

    def link_replacer_single(match):
        raw_url = match.group(1)
        text_content = match.group(2)
        target = ""
        url = raw_url
        if url.startswith('*'):
            url = url[1:].strip()
            target = ' target="_blank"'
        if not (url.startswith('http://') or url.startswith('https://')):
             return match.group(0)
        exclude_keywords = ["已编辑", "数据删除", "无法辨认", "数据已删除", "咒骂声", "尖叫声","DATA EXPUNGED", "REDACTED", "DATA LOST", "数据丢失"]
        upper_text = text_content.upper()
        for kw in exclude_keywords:
            if kw in upper_text:
                return match.group(0) 
        return f'<a href="{url}"{target}>{text_content}</a>'

    text = re.sub(r'(?<!\[)\[(\*?\s*https?://\S+)\s+([^\]]+)\]', link_replacer_single, text, flags=re.IGNORECASE)

    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!:)//(.*?)//', r'<i>\1</i>', text)
    text = re.sub(r'\^\^(.*?)\^\^', r'<sup>\1</sup>', text, flags=re.DOTALL)
    text = re.sub(r',,(.*?),,', r'<sub>\1</sub>', text, flags=re.DOTALL)
    text = re.sub(r'__(?!\s)(.*?)(?<!\s)__', r'<u>\1</u>', text, flags=re.DOTALL)
    text = re.sub(r'--(?!\s)(.*?)(?<!\s)--', r'<s>\1</s>', text, flags=re.DOTALL)
    text = re.sub(r'\{\{(.*?)\}\}', r'<span style="font-family: \'Courier New\', monospace">\1</span>', text)
    
    text = text.replace('\n', '<br>')

    if license_phs:
         text += "".join(license_phs)

    for k in reversed(list(placeholders.keys())):
        text = text.replace(k, placeholders[k])
    
    return text