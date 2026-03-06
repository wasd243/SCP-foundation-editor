import re
import uuid
import html as _html_module
# import ComponentStore
from engine.process.interceptor.Components.register_html import handle_register_html
from engine.process.interceptor.Components.register_marker import handle_register_marker
# import ACSInterceptor
from engine.process.interceptor.Components.ACSInterceptor import process_acs

class ComponentStore:
    """组件金库：负责存储并分发所有被拦截的组件"""
    def __init__(self):
        self.components = {}

    def register_html(self, original_source: str, comp_type: str, html_shell_template: str) -> str:
        """注册并生成自定义交互 UI 外壳"""
        # 直接调用外部文件传入的逻辑，注意将 self 作为 comp 参数传入
        return handle_register_html(self, original_source, comp_type, html_shell_template)

    def register_marker(self, original_source: str, comp_type: str) -> str:
        """注册但不生成外壳，交由 ftml 原生渲染 (如 div, css, 折叠块)"""
        return handle_register_marker(self, original_source, comp_type)

    def get_all(self): return self.components
    def clear(self): self.components.clear()


class ComponentInterceptor:
    def __init__(self):
        self.store = ComponentStore()

    def intercept(self, text: str, theme_type: str, inner_parser_cb) -> tuple[str, ComponentStore]:
        self.store.clear()
        processed_text = text
        
        # 1. 基础预清理
        processed_text = re.sub(r'\[\[<\]\]\s*\[\[module Rate\]\]\s*\[\[/<\]\]', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[>\]\]\s*\[\[module Rate\]\]\s*\[\[/>\]\]', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[module Rate\]\]', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[include :scp-wiki-cn:theme:.*?\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[include :scp-wiki:component:.*?\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:betterfootnotes.*?\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[footnoteblock\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)

        # 2. 脚注
        def fn_replacer(match):
            source = match.group(0)
            content = match.group(1)
            html = f'<span class="scp-component scp-footnote" data-type="footnote" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-content="{_html_module.escape(content)}" title="{_html_module.escape(content)}" contenteditable="false">#</span>'
            return self.store.register_html(source, "footnote", html)
        processed_text = re.sub(r'\[\[footnote\]\](.*?)\[\[/footnote\]\]', fn_replacer, processed_text, flags=re.DOTALL)

        def bf_replacer(match):
            source = match.group(0)
            content = match.group(2).strip()
            html = f'<span class="scp-component scp-footnote" data-type="footnote" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-content="{_html_module.escape(content)}" title="{_html_module.escape(content)}" contenteditable="false">#</span>'
            return self.store.register_html(source, "footnote", html)
        processed_text = re.sub(r'\[\[span\s+class=["\']fnnum["\']\]\](.*?)\[\[/span\]\]\[\[span\s+class=["\']fncon["\']\]\](.*?)\[\[/span\]\]', bf_replacer, processed_text, flags=re.DOTALL)

        # 3. 授权引用 (完美还原文件解析)
        def license_replacer(match):
            source = match.group(0)
            author_m = re.search(r'\|author=([^\|\n\]]+)', source)
            translator_m = re.search(r'\|translator=([^\|\n\]]+)', source)
            lang_m = re.search(r'\|lang=CN', source, re.IGNORECASE)
            
            author = author_m.group(1).strip() if author_m else ""
            translator = translator_m.group(1).strip() if translator_m else ""
            is_original = lang_m is not None
            
            files_content_im = re.search(r'=====(.*?)=====', source, flags=re.DOTALL)
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
                    elif content.startswith('**图像名：**'): current_file['img_name'] = content.replace('**图像名：**', '').strip()
                    elif content.startswith('**图像作者：**'): current_file['img_author'] = content.replace('**图像作者：**', '').strip()
                    elif content.startswith('**作者：**'): current_file['img_author'] = content.replace('**作者：**', '').strip()
                    elif content.startswith('**授权协议：**'): current_file['img_license'] = content.replace('**授权协议：**', '').strip()
                    elif content.startswith('**来源链接：**'): current_file['source_link'] = content.replace('**来源链接：**', '').strip()
                    elif content.startswith('来源链接：'): current_file['source_link'] = content.replace('来源链接：', '').strip()
                    elif content.startswith('**衍生自：**'): current_file['derived_from'] = content.replace('**衍生自：**', '').strip()
                    elif content.startswith('**备注：**'): current_file['note'] = content.replace('**备注：**', '').strip()
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
            html = f'''<div class="scp-component license-box open" data-type="license" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-original="{orig_attr}" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)<button class="btn-license-original{orig_btn_cls}" onclick="toggleLicenseOriginal(this, event)" title="原创：生成|lang=CN，并取消|translator">原创</button></div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true">{author}</span></div><div class="license-field-row license-translator-row{trans_row_cls}"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true">{translator}</span></div><hr><div class="extra-files-container">{files_html}</div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>'''
            return self.store.register_html(source, "license", html)

        processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\].*?\[\[include :scp-wiki-cn:component:license-box-end\]\]', license_replacer, processed_text, flags=re.DOTALL)
        processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box-end.*?\]\]', '', processed_text)
        processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\]', '', processed_text, flags=re.DOTALL)

        # 4. ACS 异常分级
        processed_text = process_acs(processed_text, self.store)

        # 5. AIM
        def aim_replacer(match):
            source = match.group(0)
            def get_arg(name):
                m = re.search(fr'(?:\||\s+)\s*{name}\s*=\s*([^\|\n\]]+)', source, re.IGNORECASE)
                return m.group(1).strip() if m else "???"
            blocks_arg = get_arg('blocks')
            row_style_top = 'display:none;' if blocks_arg == '!' else ''
            row_style_bottom = 'display:none;' if blocks_arg == '-' else ''
            html = f'''<div class="scp-component aim-box" data-type="aim" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-blocks="{blocks_arg}" contenteditable="false"><table class="aim-table"><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">项目编号</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">{get_arg('XXXX')}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">等级 / 公开</div><div class="aim-value" data-field="lv" contenteditable="true">{get_arg('lv')}</div></td></tr><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">收容等级</div><div class="aim-value" data-field="cc" contenteditable="true">{get_arg('cc')}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">扰动等级</div><div class="aim-value" data-field="dc" contenteditable="true">{get_arg('dc')}</div></td></tr><tr style="{row_style_bottom} text-align: center; background: #fafafa;"><td><div class="aim-label">负责站点</div><div class="aim-value" data-field="site" contenteditable="true">{get_arg('site')}</div></td><td><div class="aim-label">站点主管</div><div class="aim-value" data-field="dir" contenteditable="true">{get_arg('dir')}</div></td><td><div class="aim-label">首席研究员</div><div class="aim-value" data-field="head" contenteditable="true">{get_arg('head')}</div></td><td><div class="aim-label">指派特遣队</div><div class="aim-value" data-field="mtf" contenteditable="true">{get_arg('mtf')}</div></td></tr></table><div class="aim-footer">AIM Module</div></div>'''
            return self.store.register_html(source, "aim", html)
        processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:advanced-information-methodology.*?\]\]', aim_replacer, processed_text, flags=re.DOTALL)

        # 6. 图片块
        def wrap_center(m):
            content = m.group(1)
            if re.search(r'align=[^|\]\n]+', content, re.IGNORECASE): content = re.sub(r'align=[^|\]\n]+', 'align=center', content, flags=re.IGNORECASE)
            else: content = content.replace(']]', ' |align=center]]')
            return content
        processed_text = re.sub(r'\[\[=\]\]\s*(\[\[include component:image-block.*?\]\])\s*\[\[/=\]\]', wrap_center, processed_text, flags=re.DOTALL | re.IGNORECASE)

        def img_replacer(match):
            source = match.group(0)
            def get_arg(name): 
                m = re.search(fr'(?:\||\s+)\s*{name}\s*=\s*([^\|\n\]]+)', source, re.IGNORECASE)
                return m.group(1).strip() if m else ""
            name, caption, width, height, align = get_arg('name'), get_arg('caption'), get_arg('width'), get_arg('height'), get_arg('align') or 'right'
            img_style = "max-width:100%; display:block; margin:0 auto 5px auto;"
            if width: img_style += f" width:{width.lower().strip() if width.endswith(('px','%')) else width+'px'};"
            if height: img_style += f" height:{height.lower().strip() if height.endswith(('px','%')) else height+'px'};"
            if align == 'center': img_style += " width:100% !important;"
            dim_html = f'''<div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div style="display:flex; align-items:center;"><b style="flex-shrink:0;">源: &nbsp;</b><span data-field="name" style="display:none;">{name}</span><span class="img-link-label" onclick="editImgLink(this)" onmousedown="event.stopPropagation();" style="color:blue; text-decoration:underline; cursor:pointer;">链接</span></div><div style="display:flex; justify-content:space-between; align-items:baseline;"><span><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{width}</span></span> <span><b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{height}</span></span></div></div>'''
            html = f'''<div class="scp-component image-block-box" data-type="image-block-adv" data-align="{align}" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'center')" onmousedown="event.stopPropagation();">置中</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div>{dim_html}</div><div class="image-block-content"><img src="{name}" class="img-preview" style="{img_style}"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;display:none;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">{caption}</span></div></div>'''
            return self.store.register_html(source, "image-block", html)
        processed_text = re.sub(r'\[\[include component:image-block.*?\]\]', img_replacer, processed_text, flags=re.DOTALL)

        # 7. Tabview
        def tabview_replacer(match):
            source = match.group(0)
            content = match.group(1)
            tabs = re.findall(r'\[\[tab ([^\]]+)\]\](.*?)\[\[/tab\]\]', content, flags=re.DOTALL)
            header_html, body_html = "", ""
            for i, (title, body) in enumerate(tabs):
                active = " active" if i == 0 else ""
                header_html += f'<span class="tab-btn{active}" contenteditable="true" onclick="selectTab(this)">{title.strip()}</span>'
                body_html += f'<div class="tab-item{active}" contenteditable="true">{inner_parser_cb(body, theme_type)}</div>'
            html = f'''<div class="scp-component tabview-box" data-type="tabview" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false"><div class="tab-header">{header_html}<span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents">{body_html}</div></div>'''
            return self.store.register_html(source, "tabview", html)
        processed_text = re.sub(r'\[\[tabview\]\](.*?)\[\[/tabview\]\]', tabview_replacer, processed_text, flags=re.DOTALL)

        # 8. 用户信息 (User) - 【完美修复】使用 flexbox 彻底解决星星由于行内元素排版断裂的问题
        def user_replacer(match):
            source = match.group(0)
            name = match.group(1).strip()
            html = f'<span class="scp-component user-tag" data-type="user" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false" style="display:inline-flex; align-items:center; gap:4px; padding:0 2px;"><span class="user-icon" style="background:#aaa; display:inline-block; width:12px; height:12px; border-radius:50%;"></span><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{_html_module.escape(name)}</span></span>'
            return self.store.register_html(source, "user", html)
        processed_text = re.sub(r'\[\[user\s+([^\]]+)\]\]', user_replacer, processed_text, flags=re.IGNORECASE)

        def user_adv_replacer(match):
            source = match.group(0)
            name = match.group(1).strip()
            html = f'<span class="scp-component user-tag" data-type="user-adv" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false" style="display:inline-flex; align-items:center; gap:4px; padding:0 2px;"><span class="user-icon" style="background:gold; display:inline-flex; justify-content:center; align-items:center; width:14px; height:14px; border-radius:50%; color:#fff; font-size:10px;">★</span><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{_html_module.escape(name)}</span></span>'
            return self.store.register_html(source, "user-adv", html)
        processed_text = re.sub(r'\[\[\*user\s+([^\]]+)\]\]', user_adv_replacer, processed_text, flags=re.IGNORECASE)

        # 8-B. 登入登出 (Fakeprot) - ftml无法完全原生识别其复杂DOM，直接放入组件拦截
        def process_fakeprot_source(txt):
            result = []
            cursor = 0
            pat_div_start = re.compile(r'\[\[div\s+class=["\']fakeprot["\']\]\]', re.IGNORECASE)
            pat_div_close = re.compile(r'\[\[/div\]\]', re.IGNORECASE)
            pat_coll = re.compile(r'\s*\[\[collapsible\s+show="([^"]*)"\s+hide="([^"]*)"\]\](.*?)\[\[/collapsible\]\]', re.DOTALL | re.IGNORECASE)

            for m_start in pat_div_start.finditer(txt):
                div_start = m_start.start()
                if div_start < cursor: continue
                depth = 1; i = m_start.end(); div_end = None
                while i < len(txt) and depth > 0:
                    next_open = re.search(r'\[\[div', txt[i:], re.IGNORECASE)
                    next_close = pat_div_close.search(txt[i:])
                    if not next_close: break
                    pos_close = i + next_close.start()
                    pos_open = i + next_open.start() if next_open else -1
                    if next_open and pos_open < pos_close:
                        depth += 1; i = pos_open + 5
                    else:
                        depth -= 1; i = pos_close + 8
                        if depth == 0: div_end = i
                if div_end is None: continue

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

                parsed_coll = inner_parser_cb(coll_content_raw.strip(), theme_type)

                ll_html = (
                    '<div class="scp-component login-logout-box" data-type="login-logout" data-source-uuid="{{uuid}}" data-source="{{source}}" contenteditable="false" style="border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;">'
                    '<table class="login-form-table" contenteditable="false" style="margin:0.5em auto; border-collapse:collapse;"><tr>'
                    '<td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">ID</td>'
                    f'<td><span class="login-id-value" contenteditable="true" data-field="id" style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;">{id_val}</span></td></tr>'
                    '<tr><td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">密码</td>'
                    '<td><span contenteditable="false" style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif; color:#555; letter-spacing:2px;">・・・・・・・・・</span></td></tr>'
                    '<tr><td contenteditable="false"></td><td style="text-align:center;" contenteditable="false"><button contenteditable="false" style="padding:2px 18px; border:1px solid #aaa; background:#f4f4f4;  font-family:sans-serif;">登入</button></td></tr></table>'
                    '<hr contenteditable="false" style="border:none; border-top:1px solid #ccc; margin:6px 0;">'
                    '<div contenteditable="false" style="font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;">[登入]↔[登出] 折叠内容</div>'
                    f'<div class="login-collapsible-content" contenteditable="true" style="min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;">{parsed_coll}</div></div>'
                )
                source = txt[div_start:block_end]
                result.append(txt[cursor:div_start])
                result.append(self.store.register_html(source, "login-logout", ll_html))
                cursor = block_end

            result.append(txt[cursor:])
            return ''.join(result)
            
        processed_text = process_fakeprot_source(processed_text)

        # 9. 折叠块 (Collapsible) - 暂时交给 ftml 原生解析，不注入 UUID
        def process_collapsibles(txt):
            # 暂时关闭检测用户输入的注入，交给 ftml 反向解析
            pass
            return txt
        processed_text = process_collapsibles(processed_text)

        # 10. DIV 拦截与原生 UUID 注入 - 暂时交给 ftml 原生解析，不注入 UUID
        def process_divs(txt):
            # 暂时关闭检测用户输入的注入，交给 ftml 反向解析
            pass
            return txt
        processed_text = process_divs(processed_text)

        # 11. CSS 拦截与注入 - 暂时交给 ftml 原生解析，不注入 UUID
        def css_replacer(match):
            pass
        # 暂时跳过正则表达式替换，保留原样
        # processed_text = re.sub(r'\[\[module CSS\]\](.*?)\[\[/module\]\]', css_replacer, processed_text, flags=re.DOTALL|re.IGNORECASE)

        return processed_text, self.store