import os
import json
from PyQt6.QtWidgets import QInputDialog

# 获取当前文件所在的目录 (即 controllers/open_editor)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取上一级目录 (即 controllers/)，这样才能正确找到公共的 js 文件夹
CONTROLLERS_DIR = os.path.dirname(CURRENT_DIR)

def handle_open_audio_link_editor(ui, _element_id):
    """处理音频播放器链接的编辑逻辑"""
    
    js_get = "window._currentAudioLink ? window._currentAudioLink.nextElementSibling.innerText : ''"
    
    def on_got_link(content):
        if content is None: 
            content = ""
            
        # 弹出输入框
        new_text, ok = QInputDialog.getText(ui, "编辑音频链接", "请输入音频 URL:", text=content)
        
        if ok:
            # 1. 使用正确的路径：controllers/js/open_audio_link_editor.js
            js_path = os.path.join(CONTROLLERS_DIR, 'js', 'open_audio_link_editor.js')
            try:
                with open(js_path, 'r', encoding='utf-8') as f:
                    js_template = f.read()
                
                # 2. 安全转义
                safe_url = json.dumps(new_text)
                
                # 3. 替换占位符
                final_js = js_template.replace('__NEW_URL__', safe_url)
                
                # 4. 执行
                ui.browser.page().runJavaScript(final_js)
                
            except Exception as e:
                print(f"读取 JS 模板失败 ({js_path}): {e}")

    # 【关键修复】：将局部函数挂载到 ui 实例上，防止被 Python 垃圾回收机制(GC)误杀
    ui._audio_link_callback = on_got_link
    ui.browser.page().runJavaScript(js_get, ui._audio_link_callback)