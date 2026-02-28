import os
import json
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMessageBox, QDialog, 
    QInputDialog, QColorDialog, QMenu, QFileDialog
)
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QCursor

# UI导入
from ui.main_window_view import setup_main_ui
# =========================================================
# 修复 1：这里全部改成带有 handle_ 前缀的函数名
# =========================================================
from controllers.toolbar_controller import (
    sync_toolbar_state, execute_format, handle_apply_relative_size, handle_set_heading,
    handle_open_link_dialog, handle_apply_font_size, handle_choose_color, handle_clear_color,
    handle_insert_audio, handle_insert_component, handle_copy_to_clipboard, handle_update_theme_state,
    handle_insert_new_footnote
)
# 导入自定义组件
from ui.widgets.LinkDialog import LinkDialog
from ui.widgets.SaveConfirmDialog import SaveConfirmDialog
from ui.widgets.ClearConfirmDialog import ClearConfirmDialog
# 导入HTML模板
from css_styles.html_template import EDITOR_HTML
# 导入解析器主程序
from utils.wikidot_parser import parse_wikidot_code, parse_wikidot_to_editor_html
# 导入css组件注入器
from utils.component_injector import (
    inject_terminal_shortcut, inject_terminal_001, inject_raisa_notice,
    inject_class_warning, inject_foundation_background, inject_o5_command,
    inject_video_record, inject_video_record2, inject_page_note,
    inject_email_template, inject_login_logout
)
# wikidot源代码导出器
from utils.wikidot_exporter import export_html_to_wikidot
# html字典
from utils.html_templates import COMPONENT_TEMPLATES, get_aim_template
# 保存文件为.txt格式
from controllers.initiate_save import initiate_save
# 从桌面导入.txt文件
from controllers.read_from_desktop import read_from_desktop
# 矫正导入
from ui.toggle.toggle_config_panels import toggle_panels
from ui.toggle.toggle_right_dock import toggle_right_dock
from ui.toggle.on_basalt_toggled import on_basalt_toggled
from ui.toggle.on_shivering_toggled import on_shivering_toggled
from ui.toggle.on_bhl_toggled import on_bhl_toggled

class SCPEditor(QMainWindow):
    def sync_toolbar(self, state):
        """将状态同步的任务交接给外部控制器"""
        sync_toolbar_state(self, state)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCP Foundation Wiki 编辑器")
        self.resize(1400, 950)

        # 全局状态 (未来可以放进 core 文件夹进行状态管理)
        self.page_theme_config = {
            "type": "none",
            "options": []
        }
        self.use_better_footnotes = False
        self.is_saving_mode = False

        # 一键调用外部的 UI 渲染器！
        setup_main_ui(self)

    def initiate_save(self):
        initiate_save(self)
        
    def read_from_desktop(self):
        read_from_desktop(self)

    def init_editor_html(self):
        self.browser.setHtml(EDITOR_HTML)

    def toggle_config_panels(self):
        toggle_panels(self)

    def toggle_right_dock(self):
        toggle_right_dock(self)

    def on_basalt_toggled(self, checked):
        on_basalt_toggled(self, checked)
        self.update_theme_state()

    def on_shivering_toggled(self, checked):
        on_shivering_toggled(self, checked)
        self.update_theme_state()

    def on_bhl_toggled(self, checked):
        on_bhl_toggled(self, checked)
        self.update_theme_state()

    def on_bhl_office_toggled(self, checked):
        self.update_theme_state()

    # =========================================================
    # 修复 2：这里的转发调用全部加上 handle_ 前缀
    # =========================================================
    def apply_relative_size(self):
        handle_apply_relative_size(self)

    def set_heading(self, index):
        handle_set_heading(self, index)

    def open_link_dialog(self):
        handle_open_link_dialog(self)

    def exec_format(self, command, value=None):
        execute_format(self, command, value)

    def apply_font_size(self, size_str=None):
        handle_apply_font_size(self, size_str)

    def choose_color(self):
        handle_choose_color(self)

    def clear_color(self):
        handle_clear_color(self)

    def insert_audio(self):
        handle_insert_audio(self)

    # =========================================================

    def insert_hr(self):
        self.run_insert_js('<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div><p><br></p>')

    def insert_toc(self):
        self.run_insert_js('<div class="scp-component" data-type="toc" contenteditable="false" style="border: 1px dashed #999; padding: 5px; background: #f0f0f0;"><b>目录 (TOC)</b><br>[[toc]]</div><p><br></p>')

    def insert_table(self):
        self.browser.page().runJavaScript("insertTable();")

    # =========================================================

    def copy_to_clipboard(self):
        handle_copy_to_clipboard(self)

    def insert_component(self):
        handle_insert_component(self)

    def update_theme_state(self):
        handle_update_theme_state(self)

    def insert_new_footnote(self):
        handle_insert_new_footnote(self)

    def open_footnote_editor(self, index):
        js = f"document.querySelectorAll('.scp-footnote')[{index}].getAttribute('data-content')"
        def on_got(content):
            if content is None: content = ""
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑脚注", "内容:", content)
            if ok:
                update_js = f"""
                (function(){{
                    var fn = document.querySelectorAll('.scp-footnote')[{index}];
                    if(fn) {{
                        fn.setAttribute('data-content', {json.dumps(new_text)});
                        fn.setAttribute('title', {json.dumps(new_text)});
                        refreshFootnotes();
                    }}
                }})()
                """
                self.browser.page().runJavaScript(update_js)
        self.browser.page().runJavaScript(js, on_got)

    def open_audio_link_editor(self, _element_id):
        js = "window._currentAudioLink ? window._currentAudioLink.nextElementSibling.innerText : ''"
        def on_got_link(content):
            if content is None: content = ""
            new_text, ok = QInputDialog.getText(self, "编辑音频链接", "请输入音频 URL:", text=content)
            if ok:
                new_text_safe = new_text.replace('"', '\\"').replace("'", "\\'")
                update_js = f"""
                (function(){{
                    if (window._currentAudioLink) {{
                        var container = window._currentAudioLink.closest('.html5player-box');
                        if (container) {{
                            var hiddenSpan = container.querySelector('.html5player-url');
                            if (hiddenSpan) hiddenSpan.innerText = '{new_text_safe}';
                            var audioEl = container.querySelector('audio');
                            if (audioEl) {{
                                var sources = audioEl.querySelectorAll('source');
                                sources.forEach(function(s) {{ s.src = '{new_text_safe}'; }});
                                audioEl.load();
                            }}
                        }}
                    }}
                }})()
                """
                self.browser.page().runJavaScript(update_js)
        self.browser.page().runJavaScript(js, on_got_link)

    def open_license_link_editor(self, element_id):
        js = f"document.getElementById('{element_id}').innerText"
        def on_got_link(content):
            if content is None: content = ""
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑来源链接", "请输入链接地址:", content)
            if ok:
                update_js = f"""
                (function(){{
                    var el = document.getElementById('{element_id}');
                    if(el) {{ el.innerText = {json.dumps(new_text)}; }}
                }})()
                """
                self.browser.page().runJavaScript(update_js)
        self.browser.page().runJavaScript(js, on_got_link)

    def run_insert_js(self, html):
        safe_html = html.replace('\n', ' ').replace("'", "\\'")
        js = f"""
        (function() {{
            var sel = window.getSelection();
            if (sel.rangeCount) {{
                var range = sel.getRangeAt(0);
                var fragment = range.createContextualFragment('{safe_html}');
                range.deleteContents();
                range.insertNode(fragment);
                if (typeof refreshFootnotes === 'function') refreshFootnotes();
            }}
        }})();
        """
        self.browser.page().runJavaScript(js)

    def prepare_context_menu(self, pos: QPoint):
        js = f"document.elementFromPoint({pos.x()}, {pos.y()}).closest('.scp-component')?.getAttribute('data-type')"
        js_table = f"!!document.elementFromPoint({pos.x()}, {pos.y()}).closest('table.wikidot-table')"
        js_tab_btn = f"!!document.elementFromPoint({pos.x()}, {pos.y()}).classList.contains('tab-btn')"
        js_fn_idx = f"(function(){{ var el = document.elementFromPoint({pos.x()}, {pos.y()}); return el ? Array.from(document.querySelectorAll('.scp-footnote')).indexOf(el.closest('.scp-footnote')) : -1; }})()"
        full_js = f"JSON.stringify({{ comp: {js}, table: {js_table}, tabBtn: {js_tab_btn}, fnIdx: {js_fn_idx} }})"
        self.browser.page().runJavaScript(full_js, lambda res: self.show_menu(pos, json.loads(res)))

    def show_menu(self, pos, res):
        menu = QMenu()
        c_type = res.get('comp')
        in_table = res.get('table')
        is_tab_btn = res.get('tabBtn')
        fn_idx = res.get('fnIdx', -1)

        paste_act = menu.addAction("粘贴")
        paste_act.triggered.connect(lambda: self.browser.page().triggerAction(QWebEnginePage.WebAction.Paste))
        menu.addSeparator()

        if fn_idx != -1:
            menu.addAction("编辑脚注").triggered.connect(lambda: self.open_footnote_editor(fn_idx))
            menu.addSeparator()

        if c_type:
            if c_type == 'tabview' and is_tab_btn:
                menu.addAction("删除该选项卡").triggered.connect(lambda: self.browser.page().runJavaScript(
                    f"removeTab(document.elementFromPoint({pos.x()}, {pos.y()}))"))
                menu.addSeparator()

            del_act = menu.addAction(f"删除该组件")
            del_act.triggered.connect(lambda: self.remove_component_at_pos(pos))

            if c_type == 'acs':
                cm = menu.addMenu("修改等级颜色 (主等级)")
                primary_classes = ["Safe", "Euclid", "Keter", "Neutralized", "Pending", "Explained", "Esoteric"]
                for cls in primary_classes:
                    act = cm.addAction(cls)
                    act.triggered.connect(lambda checked, c=cls: self.change_acs_class(pos, c))

                sm = menu.addMenu("设置次要等级")
                secondary_classes = ["Apollyon", "Archon", "Cernunnos", "Hiemal", "Tiamat", "Ticonderoga", "Thaumiel", "None"]
                for cls in secondary_classes:
                    act = sm.addAction(cls)
                    act.triggered.connect(lambda checked, c=cls: self.change_acs_secondary(pos, c))
            
            if c_type not in ['image-block', 'image-block-adv']:
                 menu.addSeparator()
                 menu.addAction("在下面换行").triggered.connect(lambda: self.insert_newline_after_component(pos))

        if c_type in ['css-module', 'div-block']:
            menu.addSeparator()
            menu.addAction("快捷代码：终端样式").triggered.connect(lambda: self.apply_terminal_shortcut(pos))
            menu.addAction("快捷代码：终端 #001").triggered.connect(lambda: self.apply_terminal_001(pos))
            menu.addAction("快捷代码：RAISA通知").triggered.connect(lambda: self.apply_raisa_notice(pos))
            menu.addAction("快捷代码：XXXX级机密").triggered.connect(lambda: self.apply_class_warning(pos))
            menu.addAction("快捷代码：O5议会命令").triggered.connect(lambda: self.apply_o5_command(pos))
            menu.addAction("快捷代码：基金会背景").triggered.connect(lambda: self.apply_foundation_background(pos))
            menu.addAction("快捷代码：视频/音频记录1").triggered.connect(lambda: self.apply_video_record(pos))
            menu.addAction("快捷代码：视频/音频记录2").triggered.connect(lambda: self.apply_video_record2(pos))
            menu.addAction("快捷代码：便签纸").triggered.connect(lambda: self.apply_page_note(pos))
            menu.addAction("快捷代码：登入/登出").triggered.connect(lambda: self.apply_login_logout(pos))
            menu.addAction("快捷代码：电子邮件模版").triggered.connect(lambda: self.apply_email_template(pos))

        if in_table:
            t_menu = menu.addMenu("表格操作")
            t_menu.addAction("增加行").triggered.connect(lambda: self.browser.page().runJavaScript("tableAction('addRow')"))
            t_menu.addAction("删除行").triggered.connect(lambda: self.browser.page().runJavaScript("tableAction('delRow')"))
            t_menu.addAction("增加列").triggered.connect(lambda: self.browser.page().runJavaScript("tableAction('addCol')"))
            t_menu.addAction("删除列").triggered.connect(lambda: self.browser.page().runJavaScript("tableAction('delCol')"))
            t_menu.addAction("向右合并 (删除竖线)").triggered.connect(lambda: self.browser.page().runJavaScript("tableAction('mergeRight')"))
            t_menu.addAction("隐藏/显示边框").triggered.connect(lambda: self.browser.page().runJavaScript("tableAction('toggleBorder')"))
            t_menu.addSeparator()
            t_menu.addAction("删除表格").triggered.connect(lambda: self.browser.page().runJavaScript("tableAction('delTable')"))

        if not c_type and not in_table:
            add_fn = menu.addAction("插入脚注")
            add_fn.triggered.connect(self.insert_new_footnote)

        menu.exec(self.browser.mapToGlobal(pos))

    def insert_newline_after_component(self, pos):
        js = f"""
        (function() {{
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box');
            if (comp) {{
                var p = document.createElement('p');
                p.innerHTML = '<br>';
                comp.parentNode.insertBefore(p, comp.nextSibling);
                var range = document.createRange();
                range.selectNodeContents(p);
                range.collapse(true);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            }}
        }})()
        """
        self.browser.page().runJavaScript(js)

    def apply_terminal_shortcut(self, pos):
        inject_terminal_shortcut(self.browser.page(), pos.x(), pos.y())
        self.check_enable_basalt.setChecked(False)
        self.check_enable_shivering.setChecked(False)
        self.check_enable_bhl.setChecked(False)
        self.update_theme_state()

    def apply_terminal_001(self, pos):
        inject_terminal_001(self.browser.page(), pos.x(), pos.y())

    def apply_raisa_notice(self, pos):
        inject_raisa_notice(self.browser.page(), pos.x(), pos.y())

    def apply_class_warning(self, pos):
        inject_class_warning(self.browser.page(), pos.x(), pos.y())

    def apply_foundation_background(self, pos):
        inject_foundation_background(self.browser.page(), pos.x(), pos.y())

    def apply_o5_command(self, pos):
        inject_o5_command(self.browser.page(), pos.x(), pos.y())

    def apply_video_record(self, pos):
        inject_video_record(self.browser.page(), pos.x(), pos.y())

    def apply_video_record2(self, pos):
        inject_video_record2(self.browser.page(), pos.x(), pos.y())

    def apply_page_note(self, pos):
        inject_page_note(self.browser.page(), pos.x(), pos.y())

    def apply_email_template(self, pos):
        inject_email_template(self.browser.page(), pos.x(), pos.y())

    def apply_login_logout(self, pos):
        inject_login_logout(self.browser.page(), pos.x(), pos.y())

    def change_acs_class(self, pos, class_name):
        self.browser.page().runJavaScript(f'applyAcsChange(document.elementFromPoint({pos.x()}, {pos.y()}), "{class_name}")')

    def change_acs_secondary(self, pos, class_name):
        val = class_name if class_name != "None" else "none"
        self.browser.page().runJavaScript(f'applyAcsSecondary(document.elementFromPoint({pos.x()}, {pos.y()}), "{val}")')

    def edit_footnote_at_pos(self, pos):
        js = f"var el = document.elementFromPoint({pos.x()}, {pos.y()}); while(el && !el.classList.contains('scp-footnote')) el = el.parentElement; el ? el.getAttribute('data-content') : ''"
        def on_got(content):
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑脚注", "内容:", content)
            if ok: self.browser.page().runJavaScript(
                f"var el = document.elementFromPoint({pos.x()}, {pos.y()}); while(el && !el.classList.contains('scp-footnote')) el = el.parentElement; if(el) {{ el.setAttribute('data-content', {json.dumps(new_text)}); refreshFootnotes(); }}")

    def remove_component_at_pos(self, pos):
        self.browser.page().runJavaScript(f"var el = document.elementFromPoint({pos.x()}, {pos.y()}).closest('.scp-component'); if(el) {{ el.remove(); refreshFootnotes(); }}")

    def toggle_auto_refresh(self, state):
        if state == Qt.CheckState.Checked.value:
            self.auto_refresh_timer.start(1500)
        else:
            self.auto_refresh_timer.stop()

    def export_wikidot(self):
        self._export_snapshot = {
            'basalt_on':    self.check_enable_basalt.isChecked(),
            'basalt_dark':  self.check_dark.isChecked(),
            'basalt_wide':  self.check_wide.isChecked(),
            'basalt_hide':  self.check_hidetitle.isChecked(),
            'shiver_on':    self.check_enable_shivering.isChecked(),
            'shiv_mo':      self.radio_shiv_mo.isChecked(),
            'shiv_kl':      self.radio_shiv_kl.isChecked(),
            'shiv_dub':     self.radio_shiv_dub.isChecked(),
            'shiv_ct':      self.radio_shiv_ct.isChecked(),
            'shiv_ba':      self.radio_shiv_ba.isChecked(),
            'bhl_on':       self.check_enable_bhl.isChecked(),
            'bhl_sidebar':  self.check_dark_sidebar.isChecked(),
            'bhl_coll':     self.check_bhl_collapsible.isChecked(),
            'bhl_toggle':   self.check_bhl_toggle.isChecked(),
            'bhl_center':   self.check_bhl_centered.isChecked(),
            'bhl_office':   self.check_bhl_office.isChecked(),
            'bf_on':        self.check_better_footnotes.isChecked(),
        }
        
        js_sync = "document.querySelectorAll('.acs-anim-checkbox, .acs-shiver-checkbox').forEach(cb => { if(cb.checked) cb.setAttribute('checked', 'checked'); else cb.removeAttribute('checked'); });"
        self.browser.page().runJavaScript(js_sync)
        
        def handle_generated_html(html):
            final_code = export_html_to_wikidot(html, self._export_snapshot)
            self.use_better_footnotes = self._export_snapshot.get('bf_on')
            self.update_theme_state()
            
            if getattr(self, 'is_saving_mode', False):
                self.is_saving_mode = False 
                dialog = SaveConfirmDialog(self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    try:
                        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                        filepath = os.path.join(desktop, "scp_draft.txt")
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(final_code)
                        QMessageBox.information(self, "成功", f"文件已保存至：\n{filepath}")
                    except Exception as e:
                        QMessageBox.warning(self, "错误", f"保存失败：{str(e)}")
            else:
                v_scrollbar = self.source_display.verticalScrollBar()
                h_scrollbar = self.source_display.horizontalScrollBar()
                v_val = v_scrollbar.value()
                h_val = h_scrollbar.value()
                self.source_display.setPlainText(final_code.strip())
                v_scrollbar.setValue(v_val)
                h_scrollbar.setValue(h_val)

        self.browser.page().toHtml(handle_generated_html)

    def render_to_editor(self):
        code = self.source_display.toPlainText()
        if not code.strip(): return

        parsed_data = parse_wikidot_code(code)
        themes = parsed_data["themes"]
        
        if themes["basalt"]:
            self.check_enable_basalt.setChecked(True)
            self.check_dark.setChecked(themes["basalt_dark"])
            self.check_wide.setChecked(themes["basalt_wide"])
            self.check_hidetitle.setChecked(themes["basalt_hidetitle"])
            self.on_basalt_toggled(True)
        elif themes["shivering_night"]:
            self.check_enable_shivering.setChecked(True)
            sub = themes["shivering_sub"]
            if sub == "macau": self.radio_shiv_mo.setChecked(True)
            elif sub == "kl": self.radio_shiv_kl.setChecked(True)
            elif sub == "dub": self.radio_shiv_dub.setChecked(True)
            elif sub == "ct": self.radio_shiv_ct.setChecked(True)
            elif sub == "ba": self.radio_shiv_ba.setChecked(True)
            else: self.radio_shiv_default.setChecked(True)
            self.on_shivering_toggled(True)
        elif themes["bhl"]:
            self.check_enable_bhl.setChecked(True)
            self.check_dark_sidebar.setChecked(themes["bhl_dark_sidebar"])
            self.check_bhl_collapsible.setChecked(themes["bhl_collapsible"])
            self.check_bhl_toggle.setChecked(themes["bhl_toggle"])
            self.check_bhl_centered.setChecked(themes["bhl_centered"])
            self.check_bhl_office.setChecked(themes["bhl_office"])
            self.on_bhl_toggled(True)
        else:
            self.check_enable_basalt.setChecked(False)
            self.check_enable_shivering.setChecked(False)
            self.check_enable_bhl.setChecked(False)
            self.on_basalt_toggled(False)

        self.check_better_footnotes.setChecked(parsed_data["better_footnotes"])
        self.update_theme_state()

        current_theme = getattr(self, "page_theme_config", {}).get("type", "none")
        html_content = parse_wikidot_to_editor_html(code, current_theme)
        
        safe_html = html_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        safe_css = parsed_data["css"].replace('`', '\\`')
        
        js = f"""
        document.getElementById('editor-root').innerHTML = "{safe_html}";
        var style = document.getElementById('dynamic-terminal-style');
        if (!style) {{
            style = document.createElement('style');
            style.id = 'dynamic-terminal-style';
            document.head.appendChild(style);
        }}
        style.textContent = `{safe_css}`; 
        if(typeof refreshFootnotes === 'function') refreshFootnotes();
        if(typeof setupObserver === 'function') setupObserver();
        """
        self.browser.page().runJavaScript(js)
        
        rate_hidden = parsed_data["rate_module"]["hidden"]
        rate_align = parsed_data["rate_module"]["align"]
        
        js_rate = f"""
        (function() {{
            const rateBox = document.querySelector('.rate-module-box');
            if (rateBox) {{
                if ({'true' if rate_hidden else 'false'}) {{
                    rateBox.classList.add('hidden-rate');
                    rateBox.setAttribute('data-hidden', 'true');
                    const hideBtn = rateBox.querySelector('.rate-btn:nth-child(2)');
                    if(hideBtn) hideBtn.innerText = '恢复';
                }} else {{
                    rateBox.classList.remove('hidden-rate');
                    rateBox.setAttribute('data-hidden', 'false');
                    const hideBtn = rateBox.querySelector('.rate-btn:nth-child(2)');
                    if(hideBtn) hideBtn.innerText = '隐藏';
                    
                    rateBox.removeAttribute('data-align');
                    rateBox.querySelectorAll('.rate-align-btn').forEach(b => b.classList.remove('active'));

                    if ('{rate_align}' === 'left') {{
                        const btn = rateBox.querySelector('.rate-align-btn:first-child');
                        if(btn) rateAction('left', btn); 
                    }} else if ('{rate_align}' === 'right') {{
                        const btn = rateBox.querySelector('.rate-align-btn:last-child');
                        if(btn) rateAction('right', btn);
                    }}
                }}
            }}
        }})();
        """
        self.browser.page().runJavaScript(js_rate)
        QMessageBox.information(self, "渲染完成", "代码已还原到编辑器。(已恢复原版所有组件和渲染格式！)")

    def clear_all_content(self):
        dialog = ClearConfirmDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.source_display.setPlainText("")
            self.check_enable_basalt.setChecked(False)
            self.check_enable_shivering.setChecked(False)
            self.check_enable_bhl.setChecked(False)
            self.check_better_footnotes.setChecked(False)
            self.page_theme_config = { "type": "none", "options": [] }
            self.heading_selector.setCurrentIndex(0)
            self.comp_selector.setCurrentIndex(0)
            self.update_theme_state()
            self.init_editor_html()
            QMessageBox.information(self, "清理完成", "编辑器内容与设置已清空。")

    def insert_basalt_div(self, class_name):
        content = "正文在此。"
        if class_name == "blockquote": label = "引用/笔记"
        elif class_name == "notation": label = "高级引用/笔记"
        elif class_name == "jotting": label = "虚线框"
        elif class_name == "modal": label = "调试用笔记"
        elif class_name == "smallmodal": label = "小号调试用笔记"
        elif "floatbox" in class_name: label = "浮动框"
        elif class_name == "raisa_memo": content = "来自记录与信息安全管理部的通知"
        elif class_name == "classification_memo": content = "分级委员会备忘录"
        elif class_name == "ettra_memo": content = "来自潜在战术威胁响应局的通知"
        elif class_name == "ethics_memo": content = "伦理委员会备忘录"
        elif class_name == "temporal_memo": content = "时间异常部门"
        elif class_name == "overwatch_memo": content = "监督者指挥部"
        elif class_name == "miscomm_memo": content = "来自误传部门的通知"
            
        pos = self.browser.mapFromGlobal(QCursor.pos())
        js = f"""
        (function(cls) {{
            var editor = document.getElementById('editor-root');
            var sel = window.getSelection();
            var range = (sel.rangeCount > 0) ? sel.getRangeAt(0) : null;
            var lb = editor.querySelector('.license-box');

            var box = document.createElement('div');
            var base_cls = cls.split(' ')[0];
            if (cls.indexOf(' ') !== -1) {{
                var parts = cls.split(' ');
                box.className = 'scp-component div-box basalt-div basalt-' + parts[0] + '-box ' + parts[1];
            }} else {{
                box.className = 'scp-component div-box basalt-div basalt-' + cls + '-box';
            }}
            if (base_cls === 'document' || base_cls === 'darkdocument') {{
                box.className += ' basalt-doc-wrapper';
            }}
            if (base_cls.indexOf('_memo') !== -1) {{
                box.className += ' basalt-memo-box';
            }}
            box.setAttribute('data-type', 'div-block');
            box.setAttribute('data-class', cls);
            box.setAttribute('contenteditable', 'false');
            
            var header = document.createElement('div');
            header.className = 'div-header';
            header.setAttribute('contenteditable', 'false');
            header.innerText = '[[div class="' + cls + '"]]';
            box.appendChild(header);

            var content = document.createElement('div');
            content.className = 'div-content';
            content.setAttribute('contenteditable', 'true');
            content.innerHTML = '<p>{content}</p>';
            box.appendChild(content);

            if (range && editor.contains(range.startContainer)) {{
                var isAfterLb = false;
                if (lb) {{
                    if (lb.contains(range.startContainer) || (range.startContainer === editor && range.startOffset >= Array.from(editor.childNodes).indexOf(lb))) {{
                        isAfterLb = true;
                    }}
                }}
                if (isAfterLb) {{ editor.insertBefore(box, lb); }} 
                else {{ range.collapse(false); range.insertNode(box); }}
            }} else {{
                var el = document.elementFromPoint({pos.x()}, {pos.y()});
                var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;

                if (comp) {{
                    if (comp.classList.contains('license-box')) {{ comp.parentNode.insertBefore(box, comp); }} 
                    else {{ comp.parentNode.insertBefore(box, comp.nextSibling); }}
                }} else {{
                    if (lb) {{ editor.insertBefore(box, lb); }} 
                    else {{ editor.appendChild(box); }}
                }}
            }}
            var br = document.createElement('br');
            box.parentNode.insertBefore(br, box.nextSibling);
            if (typeof updateBasaltDocLayout === 'function') {{ updateBasaltDocLayout(); }}
        }})('{class_name}');
        """
        self.browser.page().runJavaScript(js)