import os
import json
from PyQt6.QtWidgets import QInputDialog

# 获取当前文件所在的目录 (即 controllers/open_editor)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取上一级目录 (即 controllers/)，这样才能正确找到公共的 js 文件夹
CONTROLLERS_DIR = os.path.dirname(CURRENT_DIR)

def handle_open_license_link_editor(ui, element_id):
    """处理授权引用框中来源链接的编辑逻辑"""
    
    js_get = f"document.getElementById('{element_id}').innerText"
    
    def on_got_link(content):
        if content is None: 
            content = ""
            
        new_text, ok = QInputDialog.getMultiLineText(ui, "编辑来源链接", "请输入链接地址:", content)
        
        if ok:
            # 1. 使用正确的路径：controllers/js/open_license_link_editor.js
            js_path = os.path.join(CONTROLLERS_DIR, 'js', 'open_license_link_editor.js')
            try:
                with open(js_path, 'r', encoding='utf-8') as f:
                    js_template = f.read()
                
                # 2. 安全转义
                safe_text = json.dumps(new_text)
                
                # 3. 链式替换两个占位符：ID 和 文本内容
                final_js = js_template.replace('__ELEMENT_ID__', element_id).replace('__NEW_TEXT__', safe_text)
                
                # 4. 执行
                ui.browser.page().runJavaScript(final_js)
                
            except Exception as e:
                print(f"读取 JS 模板失败 ({js_path}): {e}")

    # 【关键修复】：将局部函数挂载到 ui 实例上，防止被 Python 垃圾回收机制(GC)误杀
    ui._license_link_callback = on_got_link
    ui.browser.page().runJavaScript(js_get, ui._license_link_callback)