import os
# 1. 获取当前 html_template.py 文件所在的文件夹绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 拼接出同目录下 editor.html 的完整路径
HTML_FILE_PATH = os.path.join(CURRENT_DIR, 'editor.html')

# 3. 读取 HTML 文件的内容，赋值给 EDITOR_HTML 变量
try:
    # 务必加上 encoding='utf-8'，防止中文乱码报错
    with open(HTML_FILE_PATH, 'r', encoding='utf-8') as f:
        EDITOR_HTML = f.read()
except Exception as e:
    print(f"[致命错误] 加载 HTML 模板失败: {e}")
    # 提供一个备用的报错网页，防止程序直接白屏崩溃
    EDITOR_HTML = f"<html><body><h1 style='color:red;'>HTML模板加载失败！</h1><p>{e}</p></body></html>"