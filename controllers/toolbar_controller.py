import json
import os
from PyQt6.QtWidgets import (
    QInputDialog, QDialog, QColorDialog, QMessageBox,
    QApplication
)
# 导入linkdialog模块
from ui.widgets.LinkDialog import LinkDialog
# 导入html转写
from utils.html_templates import (
    get_aim_template, COMPONENT_TEMPLATES
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def sync_toolbar_state(ui, state):
    """
    根据 JS 传来的状态更新工具栏按钮提示
    ui: 代表 Main.py 中的 SCPEditor 实例 (ui)
    state: JS 传来的状态字典
    """
    mapping = {
        'bold': (ui.bold_act, "加粗 (Bold)"),
        'italic': (ui.italic_act, "斜体 (Italic)"),
        'underline': (ui.underline_act, "下划线 (Underline)"),
        'strike': (ui.strike_act, "删除线 (Strikethrough)"),
        'sup': (ui.sup_act, "上标 (Superscript)"),
        'sub': (ui.sub_act, "下标 (Subscript)"),
        'mono': (ui.mono_act, "等宽字体 (Monospace)"),
        'ul': (ui.ul_act, "无序列表"),
        'ol': (ui.ol_act, "有序列表")
    }
    
    for key, (act, label) in mapping.items():
        is_on = state.get(key, False)
        act.blockSignals(True)
        act.setChecked(is_on)
        act.blockSignals(False)
        status = "[开启]" if is_on else "[关闭]"
        act.setToolTip(f"{label} {status}")
        
    # 颜色按钮状态
    color_on = state.get('color', False)
    ui.color_act.blockSignals(True)
    ui.color_act.setChecked(color_on)
    ui.color_act.blockSignals(False)
    ui.color_act.setToolTip(f"文字颜色 {'[开启]' if color_on else '[关闭]'}")

    # 同步标题选择器
    heading_idx = state.get('heading', 0)
    ui.heading_selector.blockSignals(True)
    ui.heading_selector.setCurrentIndex(heading_idx)
    ui.heading_selector.blockSignals(False)

    # 同步对齐方式
    align = state.get('align', 'left')
    ui.left_act.blockSignals(True)
    ui.left_act.setChecked(align == 'left')
    ui.left_act.blockSignals(False)
    ui.left_act.setToolTip(f"靠左 {'[开启]' if align == 'left' else '[关闭]'}")

    ui.right_act.blockSignals(True)
    ui.right_act.setChecked(align == 'right')
    ui.right_act.blockSignals(False)
    ui.right_act.setToolTip(f"靠右 {'[开启]' if align == 'right' else '[关闭]'}")


def execute_format(ui, command, value=None):
    """执行富文本格式化命令 (通过外部 JS 模板)"""
    val_str = json.dumps(value) if value is not None else "null"
    
    js_path = os.path.join(CURRENT_DIR, 'js', 'execute_format.js')
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()
            
        # 核心：连续使用 replace 替换掉 JS 文件里的两个占位符
        final_js = js_template.replace('__COMMAND__', command).replace('__VAL_STR__', val_str)
        
        ui.browser.page().runJavaScript(final_js)
        ui.browser.setFocus()
    except Exception as e:
        print(f"读取 JS 模板失败 ({js_path}): {e}")

def handle_apply_relative_size(ui):
    size_str = ui.rel_size_selector.currentText()
    if size_str == "自定义":
        val, ok = QInputDialog.getText(ui, "自定义相对字号", "请输入值 (如 2em, 200%, smaller):")
        if ok and val:
            size_str = val
        else:
            return
    ui.browser.page().runJavaScript(f"applyFontSize('{size_str}');")
    ui.browser.setFocus()

def handle_set_heading(ui, index):
    tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6"]
    if 0 <= index < len(tags):
        tag = tags[index]
        ui.exec_format("formatBlock", tag)

def handle_open_link_dialog(ui):
    dialog = LinkDialog(ui)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        url, text, new_window = dialog.get_data()
        if url:
            display_text = text if text else url
            target_attr = ' target="_blank"' if new_window else ''
            html = f'<a href="{url}"{target_attr}>{display_text}</a>'
            ui.browser.page().runJavaScript(f"document.execCommand('insertHTML', false, '{html}');")

def handle_apply_font_size(ui, size_str=None):
    if not size_str: size_str = ui.size_selector.currentText()
    if size_str == "自定义px":
        px, ok = QInputDialog.getText(ui, "自定义字号", "请输入像素值:")
        if ok:
            size_str = px if 'px' in px else px + 'px'
        else:
            return
    ui.browser.page().runJavaScript(f"applyFontSize('{size_str}');")
    ui.browser.setFocus()

def handle_choose_color(ui):
    color = QColorDialog.getColor()
    if color.isValid(): ui.exec_format("foreColor", color.name())

def handle_clear_color(ui):
    js_path = os.path.join(CURRENT_DIR, 'js', 'clear_color.js')
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_clear_color = f.read()
        ui.browser.page().runJavaScript(js_clear_color)
        ui.browser.setFocus()
    except Exception as e:
        print(f"读取或执行 JS 失败: {e}")

def handle_insert_audio(ui):
    html_path = os.path.join(CURRENT_DIR, 'html', 'insert_audio.html')
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            audio_html = f.read()
        ui.run_insert_js(audio_html.replace('\n', ''))
    except Exception as e:
        print(f"读取或执行 HTML 失败: {e}")

def handle_insert_component(ui):
    comp = ui.comp_selector.currentText()
    html = ""

    if comp == "版式":
        ui.update_theme_state()
        QMessageBox.information(ui, "版式更新", "版式设置已更新！请查看右侧面板确认状态。")
        return
    elif comp == "AIM 高级信息方法论":
        mode = "full"
        if ui.radio_aim_top.isChecked(): mode = "-"
        elif ui.radio_aim_bottom.isChecked(): mode = "!"
        html = get_aim_template(mode)
    elif comp == "授权引用 (License Box)":
        ui.browser.page().runJavaScript("insertLicenseBox()")
        return
    elif comp == "脚注 (Footnote)":
        ui.insert_new_footnote()
        return
    else:
        html = COMPONENT_TEMPLATES.get(comp, "")

    if html:
        safe_html = html.replace('\n', ' ').replace("'", "\\'")
            
        # 1. 动态获取 JS 文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_dir, 'js', 'insert_component.js')
    
        try:
        # 2. 读取 JS 模板
            with open(js_path, 'r', encoding='utf-8') as f:
               js_template = f.read()
                
            # 3. 核心：用真正的 HTML 替换掉模板里的占位符
            final_js = js_template.replace('__SAFE_HTML__', safe_html)
    
            # 4. 执行
            ui.browser.page().runJavaScript(final_js)
            
        except Exception as e:
            print(f"读取组件插入 JS 模板失败: {e}")

        ui.update_theme_state()

def handle_copy_to_clipboard(ui):
    clipboard = QApplication.clipboard()
    clipboard.setText(ui.source_display.toPlainText())
    QMessageBox.information(ui, "成功", "代码已复制到剪切板！")

def handle_update_theme_state(ui):
        if not hasattr(ui, 'lbl_bf_status') or not hasattr(ui, 'lbl_theme_status'):
             return

        ui.use_better_footnotes = ui.check_better_footnotes.isChecked()
        bf_text = "开启" if ui.use_better_footnotes else "关闭"
        ui.lbl_bf_status.setText(f"<b>Better Footnotes:</b> {bf_text}")

        ui.browser.page().runJavaScript("if(document.getElementById('basalt-logo-overlay')) document.getElementById('basalt-logo-overlay').style.display='none';")
        ui.browser.page().runJavaScript("document.body.classList.remove('bhl-theme');")
        ui.browser.page().runJavaScript("if(document.getElementById('editor-root')) { document.getElementById('editor-root').classList.remove('bhl-theme'); document.getElementById('editor-root').classList.remove('basalt-theme'); document.getElementById('editor-root').classList.remove('shivering-theme'); }")

        if ui.check_enable_basalt.isChecked():
            ui.page_theme_config["type"] = "basalt"
            opts = []
            if ui.check_dark.isChecked(): opts.append("darkmode=a")
            if ui.check_wide.isChecked(): opts.append("wide=a")
            if ui.check_hidetitle.isChecked(): opts.append("hidetitle=a")
            ui.page_theme_config["options"] = opts

            theme_text = "玄武岩 (Basalt)"
            if opts:
                theme_text += f"<br>选项: {', '.join(opts)}"
            ui.lbl_theme_status.setText(f"<b>当前版式:</b> {theme_text}")

            ui.browser.page().runJavaScript("if(document.getElementById('basalt-logo-overlay')) document.getElementById('basalt-logo-overlay').style.display='block';")
            ui.browser.page().runJavaScript("document.getElementById('editor-root').classList.add('basalt-theme');")
            ui.browser.page().runJavaScript("document.body.classList.remove('bhl-theme');")
            ui.browser.page().runJavaScript("document.getElementById('editor-root').classList.remove('bhl-theme');")
            ui.basalt_extra_group.setVisible(True)
 
        elif ui.check_enable_shivering.isChecked():
            ui.basalt_extra_group.setVisible(False)
            ui.page_theme_config["type"] = "shivering"
            ui.page_theme_config["options"] = [] 
            
            sub_text = "默认"
            code_suffix = ""
            if ui.radio_shiv_mo.isChecked():
                sub_text = "澳门"
                code_suffix = " mo=*"
            elif ui.radio_shiv_kl.isChecked():
                sub_text = "吉隆坡"
                code_suffix = " kl=*"
            elif ui.radio_shiv_dub.isChecked():
                sub_text = "都柏林"
                code_suffix = " dub=*"
            elif ui.radio_shiv_ct.isChecked():
                sub_text = "开普敦"
                code_suffix = " ct=*"
            elif ui.radio_shiv_ba.isChecked():
                sub_text = "布宜诺斯艾利斯"
                code_suffix = " ba=*"
            
            ui.page_theme_config["shivering_suffix"] = code_suffix
            ui.lbl_theme_status.setText(f"<b>当前版式:</b> 夜琉璃 ({sub_text})")
            ui.browser.page().runJavaScript("document.getElementById('editor-root').classList.add('shivering-theme');")
            ui.browser.page().runJavaScript("document.body.classList.remove('bhl-theme');")
            ui.browser.page().runJavaScript("document.getElementById('editor-root').classList.remove('bhl-theme');")
            ui.browser.page().runJavaScript("document.getElementById('editor-root').classList.remove('basalt-theme');")

        elif ui.check_enable_bhl.isChecked():
            ui.page_theme_config["type"] = "bhl"
            sub_opts = []
            if ui.check_dark_sidebar.isChecked(): sub_opts.append("暗色侧边栏")
            if ui.check_bhl_collapsible.isChecked(): sub_opts.append("可折叠侧边栏")
            if ui.check_bhl_toggle.isChecked(): sub_opts.append("切换侧边栏")
            if ui.check_bhl_centered.isChecked(): sub_opts.append("居中页眉")
            if ui.check_bhl_office.isChecked(): sub_opts.append("办公室")
            
            theme_text = "黑色标记笔 (Black Highlighter)"
            if sub_opts:
                theme_text += f"<br>选项: {', '.join(sub_opts)}"
            ui.lbl_theme_status.setText(f"<b>当前版式:</b> {theme_text}")
            
            ui.page_theme_config["bhl_options"] = {
                "dark_sidebar": ui.check_dark_sidebar.isChecked(),
                "collapsible": ui.check_bhl_collapsible.isChecked(),
                "toggle": ui.check_bhl_toggle.isChecked(),
                "centered": ui.check_bhl_centered.isChecked(),
                "office": ui.check_bhl_office.isChecked()
            }
            ui.browser.page().runJavaScript("document.body.classList.add('bhl-theme');")
            ui.browser.page().runJavaScript("document.getElementById('editor-root').classList.add('bhl-theme');")
            ui.browser.page().runJavaScript("document.getElementById('editor-root').classList.remove('basalt-theme');")

        else:
            ui.basalt_extra_group.setVisible(False)
            ui.page_theme_config["type"] = "none"
            ui.page_theme_config["options"] = []
            ui.lbl_theme_status.setText("<b>当前版式:</b> 无")

        is_ds = ui.check_enable_bhl.isChecked() and ui.check_dark_sidebar.isChecked()
        sidebar_text = "开启" if is_ds else "关闭"
        if hasattr(ui, 'lbl_sidebar_status'):
             ui.lbl_sidebar_status.setText(f"<b>Dark Sidebar:</b> {sidebar_text}")

def handle_insert_new_footnote(ui):
    js_path = os.path.join(CURRENT_DIR, 'js', 'insert_new_footnote.js')
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_insert_new_footnote = f.read()
        ui.browser.page().runJavaScript(js_insert_new_footnote)
    except Exception as e:
        print(f"读取或执行 JS 失败: {e}")