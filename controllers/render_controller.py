import os
import json
from PyQt6.QtWidgets import QMessageBox

# 从解析器核心导入方法
from utils.wikidot_parser import parse_wikidot_code, parse_wikidot_to_editor_html

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_render_to_editor(ui):
    """
    核心反向解析与渲染分配调度器
    """
    code = ui.source_display.toPlainText()
    if not code.strip(): return

    # 1. 纯逻辑解析，提取元数据
    parsed_data = parse_wikidot_code(code)
    themes = parsed_data["themes"]
    
    # 2. 同步 UI 面板的勾选状态
    if themes.get("basalt"):
        ui.check_enable_basalt.setChecked(True)
        ui.check_dark.setChecked(themes.get("basalt_dark", False))
        ui.check_wide.setChecked(themes.get("basalt_wide", False))
        ui.check_hidetitle.setChecked(themes.get("basalt_hidetitle", False))
        ui.on_basalt_toggled(True)
    elif themes.get("shivering_night"):
        ui.check_enable_shivering.setChecked(True)
        sub = themes.get("shivering_sub", "default")
        if sub == "macau": ui.radio_shiv_mo.setChecked(True)
        elif sub == "kl": ui.radio_shiv_kl.setChecked(True)
        elif sub == "dub": ui.radio_shiv_dub.setChecked(True)
        elif sub == "ct": ui.radio_shiv_ct.setChecked(True)
        elif sub == "ba": ui.radio_shiv_ba.setChecked(True)
        else: ui.radio_shiv_default.setChecked(True)
        ui.on_shivering_toggled(True)
    elif themes.get("bhl"):
        ui.check_enable_bhl.setChecked(True)
        ui.check_dark_sidebar.setChecked(themes.get("bhl_dark_sidebar", False))
        ui.check_bhl_collapsible.setChecked(themes.get("bhl_collapsible", False))
        ui.check_bhl_toggle.setChecked(themes.get("bhl_toggle", False))
        ui.check_bhl_centered.setChecked(themes.get("bhl_centered", False))
        ui.check_bhl_office.setChecked(themes.get("bhl_office", False))
        ui.on_bhl_toggled(True)
    else:
        ui.check_enable_basalt.setChecked(False)
        ui.check_enable_shivering.setChecked(False)
        ui.check_enable_bhl.setChecked(False)
        ui.on_basalt_toggled(False)

    ui.check_better_footnotes.setChecked(parsed_data.get("better_footnotes", False))
    ui.update_theme_state()

    # 3. 将 Wikidot 源码转换为 HTML 组件
    current_theme = getattr(ui, "page_theme_config", {}).get("type", "none")
    html_content = parse_wikidot_to_editor_html(code, current_theme)
    
    # 4. 准备动态注入数据
    css_content = parsed_data.get("css", "")
    rate_hidden = parsed_data["rate_module"]["hidden"]
    rate_align = parsed_data["rate_module"]["align"]
    
    # 5. 加载 JS 模板并注入浏览器
    js_path = os.path.join(CURRENT_DIR, 'js', 'render_inject.js')
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()

        # 安全转义一切不可控字符
        safe_html = json.dumps(html_content)
        safe_css = json.dumps(css_content)
        safe_rate_hidden = "true" if rate_hidden else "false"
        safe_rate_align = json.dumps(rate_align)

        # 链式替换所有占位符
        final_js = (js_template
                    .replace('__SAFE_HTML__', safe_html)
                    .replace('__SAFE_CSS__', safe_css)
                    .replace('__RATE_HIDDEN__', safe_rate_hidden)
                    .replace('__RATE_ALIGN__', safe_rate_align))

        ui.browser.page().runJavaScript(final_js)
        QMessageBox.information(ui, "渲染完成", "代码已还原到编辑器。(已恢复原版所有组件和渲染格式！)")

    except Exception as e:
        print(f"读取渲染 JS 模板失败 ({js_path}): {e}")
        QMessageBox.warning(ui, "渲染错误", f"界面注入失败: {e}")