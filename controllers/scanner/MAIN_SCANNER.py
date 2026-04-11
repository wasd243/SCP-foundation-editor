import re

def scan_code(ui):
    """扫描源代码内容"""
    import json

    if getattr(ui, 'source_editor_window', None) is None:
        return
    if getattr(ui, 'source_display', None) is None:
        print("⚠️ 警告：ui.source_display 不存在")
        return

    code_content = ui.source_display.toPlainText()

    # 使用第一个正则表达式匹配CSS类选择器
    css_pattern = re.compile(r'^\s*\.([a-zA-Z0-9_-]+)', re.MULTILINE)
    css_matches = css_pattern.findall(code_content)
    if css_matches:
        print("找到CSS类选择器:")
        for css in css_matches:
            print(f" - CSS类: {css}")

    # 使用第二个正则表达式匹配div标签及其class属性
    div_pattern = re.compile(r'\[\[div\s+class="([^"]+)"')
    div_matches = div_pattern.findall(code_content)
    if div_matches:
        print("找到div标签的class属性:")
        for div in div_matches:
            print(f" - div class: {div}")
