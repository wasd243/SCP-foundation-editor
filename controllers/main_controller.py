#  Copyright (C) 2026  wasd243
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  特别说明：本项目涉及的 SCP 基金会相关组件及版式遵循 CC BY-SA 3.0 协议。
#  版权信息声明：
#  本项目涉及的 SCP 基金会相关组件及版式遵循 CC BY-SA 3.0 协议。

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

# 各类控制器导入
from controllers.menu_controller import handle_prepare_context_menu
from controllers.render_controller import handle_render_to_editor
from controllers.run_insert_js import handle_run_insert_js
from controllers.insert_basalt_div import handle_insert_basalt_div

from controllers.toolbar_controller import (
    sync_toolbar_state, execute_format, handle_apply_relative_size, handle_set_heading,
    handle_open_link_dialog, handle_apply_font_size, handle_choose_color, handle_clear_color,
    handle_insert_audio, handle_insert_component, handle_copy_to_clipboard, handle_update_theme_state,
    handle_insert_new_footnote, handle_clear_all_content
)

# 导入各类独立编辑器
from controllers.open_editor.open_footnote_editor import handle_open_footnote_editor
from controllers.open_editor.open_audio_link_editor import handle_open_audio_link_editor
from controllers.open_editor.open_license_link_editor import handle_open_license_link_editor

# 导入自定义组件与样式
from ui.widgets.LinkDialog import LinkDialog
from ui.widgets.SaveConfirmDialog import SaveConfirmDialog

from ui.css_styles.html_template import EDITOR_HTML

# 核心解析器与导出器
from utils.wikidot_parser import parse_wikidot_code, parse_wikidot_to_editor_html
from utils.wikidot_exporter import export_html_to_wikidot
from utils.html_templates import COMPONENT_TEMPLATES, get_aim_template

# 杂项逻辑包
from controllers.initiate_save import initiate_save
from controllers.read_from_desktop import read_from_desktop
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

        # 全局状态
        self.page_theme_config = {
            "type": "none",
            "options": []
        }
        self.use_better_footnotes = False
        self.is_saving_mode = False

        # 初始化UI
        setup_main_ui(self)

    # ================= UI 切换事件 =================
    def toggle_config_panels(self): toggle_panels(self)
    def toggle_right_dock(self): toggle_right_dock(self)
    def on_basalt_toggled(self, checked):
        on_basalt_toggled(self, checked)
        self.update_theme_state()
    def on_shivering_toggled(self, checked):
        on_shivering_toggled(self, checked)
        self.update_theme_state()
    def on_bhl_toggled(self, checked):
        on_bhl_toggled(self, checked)
        self.update_theme_state()
    def on_bhl_office_toggled(self, checked): self.update_theme_state()

    # ================= 工具栏逻辑转发 =================
    def apply_relative_size(self): handle_apply_relative_size(self)
    def set_heading(self, index): handle_set_heading(self, index)
    def open_link_dialog(self): handle_open_link_dialog(self)
    def exec_format(self, command, value=None): execute_format(self, command, value)
    def apply_font_size(self, size_str=None): handle_apply_font_size(self, size_str)
    def choose_color(self): handle_choose_color(self)
    def clear_color(self): handle_clear_color(self)
    def insert_audio(self): handle_insert_audio(self)
    def copy_to_clipboard(self): handle_copy_to_clipboard(self)
    def insert_component(self): handle_insert_component(self)
    def update_theme_state(self): handle_update_theme_state(self)

    # ================= 基础插入与编辑器事件 =================
    def insert_hr(self):
        self.run_insert_js('<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div><p><br></p>')
    def insert_toc(self):
        self.run_insert_js('<div class="scp-component" data-type="toc" contenteditable="false" style="border: 1px dashed #999; padding: 5px; background: #f0f0f0;"><b>目录 (TOC)</b><br>[[toc]]</div><p><br></p>')
    def insert_table(self): self.browser.page().runJavaScript("insertTable();")
    
    def run_insert_js(self, html): handle_run_insert_js(self, html)
    def insert_basalt_div(self, class_name): handle_insert_basalt_div(self, class_name)

    # ================= 独立子编辑器组件 =================
    def insert_new_footnote(self): handle_insert_new_footnote(self)
    def open_footnote_editor(self, index): handle_open_footnote_editor(self, index)
    def open_audio_link_editor(self, _element_id): handle_open_audio_link_editor(self, _element_id)
    def open_license_link_editor(self, element_id): handle_open_license_link_editor(self, element_id)

    # ================= 右键菜单枢纽 =================
    def prepare_context_menu(self, pos: QPoint):
        """完全转交右键菜单的生成与逻辑判断到独立的菜单控制器"""
        # 修复：只传 self 和 pos 即可，不要传 QPoint 类本身
        handle_prepare_context_menu(self, pos)

    # ================= 存档与解析系统 =================
    def toggle_auto_refresh(self, state):
        if state == Qt.CheckState.Checked.value: self.auto_refresh_timer.start(1500)
        else: self.auto_refresh_timer.stop()
        
    def initiate_save(self): initiate_save(self)
    def read_from_desktop(self): read_from_desktop(self)
    def init_editor_html(self): self.browser.setHtml(EDITOR_HTML)
    def render_to_editor(self): handle_render_to_editor(self)

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
    # ================= 格式化系统 =================
    def clear_all_content(self):
        handle_clear_all_content(self)