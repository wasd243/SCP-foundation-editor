import re
import html as _html_module

def process_license(text: str, store) -> str:
    """
    处理授权/引用信息框 (License Box)
    将长文本块解析为带有多个可编辑表单域的 div 结构
    主要拦截 Wikidot [[include :scp-wiki-cn:component:license-box]]
    """
    processed_text = text

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
        
        return store.register_html(source, "license", html)

    processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\].*?\[\[include :scp-wiki-cn:component:license-box-end\]\]', license_replacer, processed_text, flags=re.DOTALL)
    processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box-end.*?\]\]', '', processed_text)
    processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\]', '', processed_text, flags=re.DOTALL)

    return processed_text
