import json
import os
from PyQt6.QtWidgets import (
    QInputDialog, QDialog, QColorDialog, QMessageBox,
    QApplication
)
# 导入linkdialog模块
from ui.widgets.LinkDialog import LinkDialog
# 导入html转写
from ui.widgets.html_templates import (
    get_aim_template, COMPONENT_TEMPLATES
)
# 导入clearconfirm清理确认
from ui.widgets.ClearConfirmDialog import ClearConfirmDialog

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


# =========================================================
# 🔧 修复版：带重试机制的同步核心函数
# =========================================================
def _sync_source_to_editor(ui):
    """
    将 source_display 内容推送到 CodeMirror。
    设置 _is_pushing_to_cm 标志，防止 CodeMirror 回调再触发一次同步（循环问题）。
    已增强鲁棒性：无论 runJavaScript 是否抛出异常，都会在 500ms 后通过 QTimer 释放标志位，防止永久卡死。
    """
    import json
    from PyQt6.QtCore import QTimer

    if getattr(ui, 'source_editor_window', None) is None:
        return
    if getattr(ui, 'source_display', None) is None:
        print("⚠️ 警告：ui.source_display 不存在")
        return

    code_content = ui.source_display.toPlainText()
    safe_content = json.dumps(code_content)

    print(f"🚀 [同步→CM] 推送内容长度: {len(code_content)} 字节")

    js_inject = f"""
(function() {{
    var content = {safe_content};
    console.log("🐍 Python->CM 注入，内容长度=" + content.length);
    if (typeof window.syncToEditor === 'function') {{
        window.syncToEditor(content);
    }} else {{
        console.warn("⏳ syncToEditor 尚未就绪，写入 PENDING_CONTENT");
        window.PENDING_CONTENT = content;
    }}
}})();
"""
    # 更安全的执行方式：确保在任何异常情况下都会在 finally 中释放标志
    page = ui.source_editor_window.browser.page()
    try:
        ui._is_pushing_to_cm = True
        try:
            page.runJavaScript(js_inject)
        except Exception as e:
            # 记录但不阻塞，后续 finally 保证释放标志
            print(f"JS Sync Failed: {e}")
    finally:
        # 强制在 500ms 后释放，无论成功与否
        QTimer.singleShot(500, lambda: setattr(ui, '_is_pushing_to_cm', False))


def _inject_after_load(ui, code_content):
    """等待页面加载完成后再注入，解决时序断路。"""
    import json
    from PyQt6.QtCore import QTimer

    page = ui.source_editor_window.browser.page()
    safe_content = json.dumps(code_content)

    js_inject = f"""
(function() {{
    var content = {safe_content};
    var MAX_RETRY = 20;
    var INTERVAL = 150;
    var attempt = 0;

    function trySync() {{
        attempt++;
        console.log("🔄 [重试 #" + attempt + "] 检查 syncToEditor...");
        if (typeof window.syncToEditor === 'function') {{
            window.syncToEditor(content);
            console.log("✅ [重试 #" + attempt + "] 同步成功！");
            return;
        }}
        if (attempt < MAX_RETRY) {{
            setTimeout(trySync, INTERVAL);
        }} else {{
            console.error("❌ 重试耗尽，写入 PENDING_CONTENT 兜底");
            window.PENDING_CONTENT = content;
        }}
    }}
    trySync();
}})();
"""

    def do_inject():
        print("📡 [loadFinished/Timer] 开始执行注入 JS")
        # 初始推送也标记一下，防止 CM 回调触发反向写入
        ui._is_pushing_to_cm = True
        page.runJavaScript(js_inject)
        from PyQt6.QtCore import QTimer as _QTimer
        _QTimer.singleShot(2000, lambda: setattr(ui, '_is_pushing_to_cm', False))

    try:
        page.loadFinished.connect(lambda ok: do_inject())
    except Exception:
        pass

    QTimer.singleShot(300, do_inject)


def handle_open_source_dialog(ui):
    """打开 CodeMirror 源码视窗，并建立双向同步。"""
    from code_view.main import FoundationEditor

    is_new_window = False

    if not hasattr(ui, 'source_editor_window') or ui.source_editor_window is None:
        ui.source_editor_window = FoundationEditor()
        is_new_window = True

        # ── 方向 A：source_display → CodeMirror ──────────────────────
        # source_display 内容变化时推送到 CM（已有逻辑）
        ui.source_display.textChanged.connect(lambda: _sync_source_to_editor(ui))
        print("✅ [source_dialog] 已绑定 A 向：source_display → CodeMirror")

        # ── 方向 B：CodeMirror → source_display ──────────────────────
        def _on_cm_content_changed(content: str):
            # 如果是 Python 自己刚推过去的内容触发的回调，直接跳过，防止无限循环
            if getattr(ui, '_is_pushing_to_cm', False):
                print("🔁 [防循环] Python 推送期间，跳过 CM→source_display 回写")
                return

            # 内容相同时也跳过（兜底防止无意义刷新）
            if ui.source_display.toPlainText() == content:
                return

            print(f"📨 [CM→source_display] 接收 CM 内容，长度={len(content)} 字节")

            # 阻断 textChanged 信号，防止回写触发再一次 A 向同步
            ui.source_display.blockSignals(True)
            try:
                # 保留滚动位置
                v = ui.source_display.verticalScrollBar().value()
                h = ui.source_display.horizontalScrollBar().value()
                ui.source_display.setPlainText(content)
                ui.source_display.verticalScrollBar().setValue(v)
                ui.source_display.horizontalScrollBar().setValue(h)
            finally:
                ui.source_display.blockSignals(False)

        ui.source_editor_window.bridge.content_changed.connect(_on_cm_content_changed)
        print("✅ [source_dialog] 已绑定 B 向：CodeMirror → source_display")

    ui.source_editor_window.show()
    ui.source_editor_window.activateWindow()
    ui.source_editor_window.raise_()

    # 执行初始同步（A 方向：把当前内容推入 CM）
    code_content = ui.source_display.toPlainText()
    print(f"📤 [source_dialog] 执行初始同步，内容长度={len(code_content)}")

    if is_new_window:
        _inject_after_load(ui, code_content)
    else:
        _sync_source_to_editor(ui)


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


def handle_clear_styles(ui):
    """清除选中文字的字体大小和颜色，恢复到正文样式（无标签）"""
    js_path = os.path.join(CURRENT_DIR, 'js', 'clear_styles.js')
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_clear_styles = f.read()
        ui.browser.page().runJavaScript(js_clear_styles)
        ui.browser.setFocus()
    except Exception as e:
        print(f"读取或执行 clear_styles JS 失败: {e}")


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
        if ui.radio_aim_top.isChecked():
            mode = "-"
        elif ui.radio_aim_bottom.isChecked():
            mode = "!"
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


def handle_run_scanner(ui):
    """运行正则扫描并尝试在 CodeMirror 中跳转到第一个匹配行（改为选最近/下一个）."""
    try:
        from controllers.scanner.MAIN_SCANNER import scan_code
        # 尝试获取当前源码光标位置（字符偏移），供后端选择下一个/最近匹配
        cursor_pos = None
        try:
            if hasattr(ui, 'source_display') and ui.source_display is not None:
                tc = ui.source_display.textCursor()
                cursor_pos = tc.position()
                print(f"🔎 [scanner] 当前源码光标位置（字符偏移）: {cursor_pos}")
        except Exception as e:
            print(f"无法获取 source_display 光标位置: {e}")
            cursor_pos = None

        result = scan_code(ui, cursor_pos=cursor_pos)
        return result
    except Exception as e:
        print(f"运行扫描器失败: {e}")
        return None


def handle_update_theme_state(ui):
    if not hasattr(ui, 'lbl_bf_status') or not hasattr(ui, 'lbl_theme_status'):
        return

    ui.use_better_footnotes = ui.check_better_footnotes.isChecked()
    bf_text = "开启" if ui.use_better_footnotes else "关闭"
    ui.lbl_bf_status.setText(f"<b>Better Footnotes:</b> {bf_text}")

    ui.browser.page().runJavaScript(
        "if(document.getElementById('basalt-logo-overlay')) document.getElementById('basalt-logo-overlay').style.display='none';")
    ui.browser.page().runJavaScript("document.body.classList.remove('bhl-theme');")
    ui.browser.page().runJavaScript(
        "if(document.getElementById('editor-root')) { document.getElementById('editor-root').classList.remove('bhl-theme'); document.getElementById('editor-root').classList.remove('basalt-theme'); document.getElementById('editor-root').classList.remove('shivering-theme'); }")

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

        ui.browser.page().runJavaScript(
            "if(document.getElementById('basalt-logo-overlay')) document.getElementById('basalt-logo-overlay').style.display='block';")
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


def handle_clear_all_content(ui):
    dialog = ClearConfirmDialog(ui)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        ui.source_display.setPlainText("")
        ui.check_enable_basalt.setChecked(False)
        ui.check_enable_shivering.setChecked(False)
        ui.check_enable_bhl.setChecked(False)
        ui.check_better_footnotes.setChecked(False)
        ui.page_theme_config = {"type": "none", "options": []}
        ui.heading_selector.setCurrentIndex(0)
        ui.comp_selector.setCurrentIndex(0)
        ui.update_theme_state()
        ui.init_editor_html()
        ui.reset_toc_ui()
        QMessageBox.information(ui, "清理完成", "编辑器内容与设置已清空。")
