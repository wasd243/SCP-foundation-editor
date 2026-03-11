import os
import json

# 获取当前文件所在的目录 (即 controllers 目录)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_run_insert_js(ui, html):
    """处理通用的 HTML 插入逻辑"""
    
    # 1. 动态获取 JS 文件路径
    js_path = os.path.join(CURRENT_DIR, 'js', 'run_insert_js.js')
    
    try:
        # 2. 读取 JS 模板
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()
        
        # 3. 数据安全处理 (自动处理换行符、单双引号的转义)
        safe_html = json.dumps(html)
        
        # 4. 替换占位符
        final_js = js_template.replace('__HTML_CONTENT__', safe_html)
        
        # 5. 传给浏览器执行
        ui.browser.page().runJavaScript(final_js)
        
    except Exception as e:
        print(f"读取通用插入 JS 模板失败 ({js_path}): {e}")