import json
import os
from PyQt6.QtWidgets import QInputDialog

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_open_footnote_editor(ui, index):
    """处理脚注编辑的逻辑"""
    # 这一句是单行获取逻辑，可以直接保留
    js_get = f"document.querySelectorAll('.scp-footnote')[{index}].getAttribute('data-content')"
    
    def on_got(content):
        if content is None: 
            content = ""
        new_text, ok = QInputDialog.getMultiLineText(ui, "编辑脚注", "内容:", content)
        
        if ok:
            # 1. 动态获取 JS 文件路径
            js_path = os.path.join(CURRENT_DIR, 'js', 'update_footnote.js')
            try:
                # 2. 读取 JS 模板
                with open(js_path, 'r', encoding='utf-8') as f:
                    js_template = f.read()
                
                # 3. 核心：替换占位符
                # 注意：new_text 必须经过 json.dumps 处理，这样 JS 才能正确识别换行符和引号！
                safe_text = json.dumps(new_text)
                final_js = js_template.replace('__INDEX__', str(index)).replace('__NEW_TEXT__', safe_text)
                
                # 4. 执行
                ui.browser.page().runJavaScript(final_js)
            except Exception as e:
                print(f"读取 JS 模板失败 ({js_path}): {e}")
                
    # 触发获取当前内容的 JS
    ui.browser.page().runJavaScript(js_get, on_got)