import sys
import os
import requests
import json
import re
from bs4 import BeautifulSoup, NavigableString
# 确保导入列表是干净且正确的
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox, QTabWidget,
    QMessageBox, QSplitter, QToolBar, QColorDialog, QMenu, QInputDialog,
    QCheckBox, QGroupBox, QRadioButton, QButtonGroup, QDockWidget, QFrame,
    QDialog, QFormLayout, QDialogButtonBox, QScrollArea
)
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QPoint
from PyQt6.QtGui import QAction, QIcon, QFont

# 解决部分系统图形后端报错
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"


class LinkDialog(QDialog):
    """简单的插入链接对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插入链接")
        self.layout = QFormLayout(self)

        self.url_input = QLineEdit()
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("选填，留空则显示链接")
        self.new_window_cb = QCheckBox("在新窗口打开 (*)")

        self.layout.addRow("链接地址 (URL):", self.url_input)
        self.layout.addRow("显示文本 (Text):", self.text_input)
        self.layout.addRow("", self.new_window_cb)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)

    def get_data(self):
        return self.url_input.text(), self.text_input.text(), self.new_window_cb.isChecked()


class SaveConfirmDialog(QDialog):
    """保存确认对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("保存文件")
        self.setFixedSize(300, 120)
        layout = QVBoxLayout(self)

        label = QLabel("确认保存当前文档？\n(将以 .txt 格式保存至桌面)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("确认保存")
        self.cancel_btn = QPushButton("取消")

        # 样式微调
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)


class PlainPasteTextEdit(QTextEdit):
    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)


class CustomWebPage(QWebEnginePage):
    """Custom WebPage to intercept navigation requests (for Footnote Edit)"""
    def __init__(self, parent=None, editor=None):
        super().__init__(parent)
        self.editor = editor

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Intercept "edit-footnote://" scheme
        if url.scheme() == "edit-footnote":
            # Extract index from path
            try:
                u_str = url.toString()
                idx_str = u_str.replace("edit-footnote://", "")
                if idx_str.isdigit() and self.editor:
                    self.editor.open_footnote_editor(int(idx_str))
            except Exception as e:
                print(f"Footnote navigation error: {e}")
            return False
            
        # Intercept "edit-license-link://" scheme
        if url.scheme() == "edit-license-link":
            try:
                u_str = url.toString()
                # Extract ID: remove scheme
                elem_id = u_str.replace("edit-license-link://", "")
                if elem_id and self.editor:
                    self.editor.open_license_link_editor(elem_id)
            except Exception as e:
                print(f"License link navigation error: {e}")
            return False

        return super().acceptNavigationRequest(url, _type, isMainFrame)



class SCPEditor(QMainWindow):
    """
    SCP Foundation Wiki 文档创作助手 - 功能增强版
    逻辑更新：
    - 新增：保存到桌面功能 (SaveConfirmDialog)。
    - 新增：代码反向解析功能 (wikidot_to_html_parser)，将代码还原为图形界面。
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCP Foundation Wiki 编辑器 - AIM 集成版 (增强功能)")
        self.resize(1400, 950)

        # 页面全局状态
        self.page_theme_config = {
            "type": "none",
            "options": []
        }
        self.use_better_footnotes = False

        # 用于保存流程的标记
        self.is_saving_mode = False

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 全局样式设置 ---
        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                min-height: 40px;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QComboBox {
                min-height: 35px;
                font-size: 13px;
            }
            QLineEdit {
                min-height: 35px;
                font-size: 13px;
            }
            QLabel {
                font-size: 13px;
            }
            QDockWidget {
                font-size: 13px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #aaa;
                margin-top: 10px;
                padding-top: 10px;
            }
            /* 工具栏按钮样式 */
            QToolBar QToolButton {
                width: 40px;
                height: 30px;
                font-size: 16px; 
                font-weight: bold;
                margin: 2px;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QToolBar QToolButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
            }
            /* 选中状态样式 (开启提醒) */
            QToolBar QToolButton:checked {
                background-color: #cce5ff; /* 浅蓝色背景 */
                border: 1px solid #0056b3; /* 深蓝色边框 */
                color: #000;
            }
        """)

        # --- 工具栏 ---
        toolbar = QToolBar("格式工具栏")
        toolbar.setStyleSheet("QToolBar { icon-size: 24px; spacing: 5px; }")
        main_layout.addWidget(toolbar)

        # 1. 标题选择器
        self.heading_selector = QComboBox()
        self.heading_selector.addItems([
            "正文 (P)",
            "标题 1 (+)",
            "标题 2 (++)",
            "标题 3 (+++)",
            "标题 4 (++++)",
            "标题 5 (+++++)",
            "标题 6 (++++++)"
        ])
        self.heading_selector.setMinimumWidth(120)
        self.heading_selector.currentIndexChanged.connect(self.set_heading)
        toolbar.addWidget(self.heading_selector)

        toolbar.addSeparator()

        # Save Button
        save_action = QAction("💾 保存", self)
        save_action.setToolTip("保存文档到桌面")
        save_action.triggered.connect(self.initiate_save)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # 2. 仿Word样式按钮 (设置为 checkable 以显示状态)

        # 加粗
        bold_act = QAction("B", self)
        bold_act.setToolTip("加粗 (Bold)")
        bold_font = QFont();
        bold_font.setBold(True)
        bold_act.setFont(bold_font)
        bold_act.setCheckable(True)  # 开启选中状态
        bold_act.triggered.connect(lambda: self.exec_format("bold"))
        toolbar.addAction(bold_act)

        # 斜体
        italic_act = QAction("I", self)
        italic_act.setToolTip("斜体 (Italic)")
        italic_font = QFont();
        italic_font.setItalic(True)
        italic_act.setFont(italic_font)
        italic_act.setCheckable(True)
        italic_act.triggered.connect(lambda: self.exec_format("italic"))
        toolbar.addAction(italic_act)

        # 下划线
        underline_act = QAction("U", self)
        underline_act.setToolTip("下划线 (Underline)")
        underline_font = QFont();
        underline_font.setUnderline(True)
        underline_act.setFont(underline_font)
        underline_act.setCheckable(True)
        underline_act.triggered.connect(lambda: self.exec_format("underline"))
        toolbar.addAction(underline_act)

        # 删除线
        strike_act = QAction("S", self)
        strike_act.setToolTip("删除线 (Strikethrough)")
        strike_font = QFont();
        strike_font.setStrikeOut(True)
        strike_act.setFont(strike_font)
        strike_act.setCheckable(True)
        strike_act.triggered.connect(lambda: self.exec_format("strikeThrough"))
        toolbar.addAction(strike_act)

        toolbar.addSeparator()

        # 上标
        sup_action = QAction("x²", self)
        sup_action.setToolTip("上标 (Superscript)")
        sup_action.setCheckable(True)
        sup_action.triggered.connect(lambda: self.exec_format("superscript"))
        toolbar.addAction(sup_action)

        # 下标
        sub_action = QAction("x₂", self)
        sub_action.setToolTip("下标 (Subscript)")
        sub_action.setCheckable(True)
        sub_action.triggered.connect(lambda: self.exec_format("subscript"))
        toolbar.addAction(sub_action)

        # 等宽
        mono_action = QAction("M", self)
        mono_action.setToolTip("等宽字体 (Monospace)")
        mono_font = QFont("Courier New")
        mono_action.setFont(mono_font)
        mono_action.setCheckable(True)
        mono_action.triggered.connect(lambda: self.browser.page().runJavaScript("toggleMonospace();"))
        toolbar.addAction(mono_action)

        toolbar.addSeparator()

        color_action = QAction("A", self)
        color_action.setToolTip("文字颜色")
        color_action.triggered.connect(self.choose_color)
        toolbar.addAction(color_action)

        # 插入链接
        link_action = QAction("🔗", self)
        link_action.setToolTip("插入链接")
        link_action.triggered.connect(self.open_link_dialog)
        toolbar.addAction(link_action)

        toolbar.addSeparator()

        ul_action = QAction("• List", self)
        ul_action.setToolTip("无序列表")
        ul_action.setCheckable(True)
        ul_action.triggered.connect(lambda: self.exec_format("insertUnorderedList"))
        toolbar.addAction(ul_action)

        ol_action = QAction("1. List", self)
        ol_action.setToolTip("有序列表")
        ol_action.setCheckable(True)
        ol_action.triggered.connect(lambda: self.exec_format("insertOrderedList"))
        toolbar.addAction(ol_action)

        quote_action = QAction("❝❞", self)
        quote_action.setToolTip("引用块")
        quote_action.triggered.connect(lambda: self.exec_format("formatBlock", "blockquote"))
        toolbar.addAction(quote_action)

        toolbar.addSeparator()

        hr_action = QAction("——", self)
        hr_action.setToolTip("分割线")
        hr_action.triggered.connect(self.insert_hr)
        toolbar.addAction(hr_action)

        table_action = QAction("⊞", self)
        table_action.setToolTip("表格")
        table_action.triggered.connect(self.insert_table)
        toolbar.addAction(table_action)

        toc_action = QAction("TOC", self)
        toc_action.setToolTip("目录")
        toc_action.triggered.connect(self.insert_toc)
        toolbar.addAction(toc_action)

        left_align_action = QAction("⇐", self)
        left_align_action.setToolTip("靠左")
        left_align_action.triggered.connect(lambda: self.exec_format("justifyLeft"))
        toolbar.addAction(left_align_action)

        right_align_action = QAction("⇒", self)
        right_align_action.setToolTip("靠右")
        right_align_action.triggered.connect(lambda: self.exec_format("justifyRight"))
        toolbar.addAction(right_align_action)

        toggle_dock_action = QAction("⚙️", self)
        toggle_dock_action.setToolTip("显示/隐藏页面属性")
        toggle_dock_action.setCheckable(True)
        toggle_dock_action.setChecked(True)
        toggle_dock_action.triggered.connect(self.toggle_right_dock)
        toolbar.addAction(toggle_dock_action)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- 左侧面板 ---
        left_panel = QTabWidget()
        left_panel.setStyleSheet("QTabBar::tab { height: 35px; width: 100px; font-size: 13px; }")

        comp_tab = QWidget()
        comp_layout = QVBoxLayout(comp_tab)

        # 相对字号设置
        comp_layout.addWidget(QLabel("<b>相对字号设置:</b>"))
        rel_size_layout = QHBoxLayout()
        self.rel_size_selector = QComboBox()
        self.rel_size_selector.addItems([
            "smaller", "larger", "80%", "100%", "120%", "150%", "200%", "0.8em", "1em", "1.2em", "1.5em", "2em", "自定义"
        ])
        apply_rel_size_btn = QPushButton("应用")
        apply_rel_size_btn.clicked.connect(self.apply_relative_size)
        rel_size_layout.addWidget(self.rel_size_selector)
        rel_size_layout.addWidget(apply_rel_size_btn)
        comp_layout.addLayout(rel_size_layout)

        # 绝对字号设置
        comp_layout.addWidget(QLabel("<b>绝对字号设置:</b>"))
        size_layout = QHBoxLayout()
        self.size_selector = QComboBox()
        self.size_selector.addItems([
            "xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large", "自定义px"
        ])
        apply_size_btn = QPushButton("应用字号")
        apply_size_btn.clicked.connect(lambda: self.apply_font_size())
        size_layout.addWidget(self.size_selector)
        size_layout.addWidget(apply_size_btn)
        comp_layout.addLayout(size_layout)

        comp_layout.addWidget(QLabel("<br><b>选择维基组件:</b>"))
        self.comp_selector = QComboBox()
        self.comp_selector.addItems([
            "ACS 分级系统", 
            "AIM 高级信息方法论",
            "折叠块 (Collapsible)",
            "CSS 模块",
            "DIV 模块", 
            "脚注 (Footnote)", 
            "版式", 
            "图片块 (Image Block)","高级图片块 (Advanced Image)", 
            "Tab View (选项卡)", 
            "User (用户标签)", "高级用户信息 (Advanced User)",
            "授权引用 (License Box)"
        ])
        self.comp_selector.currentIndexChanged.connect(self.toggle_config_panels)
        comp_layout.addWidget(self.comp_selector)

        # --- 版式配置 ---
        self.basalt_group = QGroupBox("版式与全局设置")
        self.basalt_group.setVisible(False)
        basalt_vbox = QVBoxLayout()

        # --- Layout Scroll Area Section ---
        # Create Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame) # Clean look
        
        # Create Container Widget & Layout
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0) # Tight margins

        # Add Better Footnotes
        self.check_better_footnotes = QCheckBox("启用 Better Footnotes (更好的脚注)")
        self.check_better_footnotes.setStyleSheet("color: red; font-weight: bold; font-size: 13px; padding: 5px;")
        self.check_better_footnotes.setToolTip("开启后将自动转换脚注格式并移除 footnoteblock")
        scroll_layout.addWidget(self.check_better_footnotes)

        # Add Basalt Theme
        self.check_enable_basalt = QCheckBox("启用玄武岩主题")
        self.check_enable_basalt.toggled.connect(self.on_basalt_toggled)
        scroll_layout.addWidget(self.check_enable_basalt)

        self.basalt_sub_options_frame = QFrame()
        self.basalt_sub_options_frame.setEnabled(False)
        self.basalt_sub_options_frame.setFrameShape(QFrame.Shape.NoFrame)
        sub_layout = QVBoxLayout(self.basalt_sub_options_frame)
        sub_layout.setContentsMargins(20, 0, 0, 0)

        self.check_dark = QCheckBox("暗色模式 (darkmode)")
        self.check_wide = QCheckBox("加宽页面 (wide)")
        self.check_hidetitle = QCheckBox("隐藏标题 (hidetitle)")

        cb_style = "QCheckBox { font-size: 13px; spacing: 8px; padding: 3px; }"
        for cb in [self.check_enable_basalt, self.check_dark, self.check_wide, self.check_hidetitle]:
            cb.setStyleSheet(cb_style)

        sub_layout.addWidget(self.check_dark)
        sub_layout.addWidget(self.check_wide)
        sub_layout.addWidget(self.check_hidetitle)

        scroll_layout.addWidget(self.basalt_sub_options_frame)

        # Add Separator
        shivering_sep = QFrame()
        shivering_sep.setFrameShape(QFrame.Shape.HLine)
        shivering_sep.setFrameShadow(QFrame.Shadow.Sunken)
        scroll_layout.addWidget(shivering_sep)

        # Add Shivering Theme
        self.check_enable_shivering = QCheckBox("启用夜琉璃版式")
        self.check_enable_shivering.setStyleSheet(cb_style)
        self.check_enable_shivering.toggled.connect(self.on_shivering_toggled)
        scroll_layout.addWidget(self.check_enable_shivering)

        self.shivering_sub_options_frame = QFrame()
        self.shivering_sub_options_frame.setEnabled(False)
        self.shivering_sub_options_frame.setFrameShape(QFrame.Shape.NoFrame)
        shivering_sub_layout = QVBoxLayout(self.shivering_sub_options_frame)
        shivering_sub_layout.setContentsMargins(20, 0, 0, 0)

        self.shivering_city_group = QButtonGroup(self)
        
        self.radio_shiv_default = QRadioButton("默认")
        self.radio_shiv_mo = QRadioButton("澳门 (Macau)")
        self.radio_shiv_kl = QRadioButton("吉隆坡 (Kuala Lumpur)")
        self.radio_shiv_dub = QRadioButton("都柏林 (Dublin)")
        self.radio_shiv_ct = QRadioButton("开普敦 (Cape Town)")
        self.radio_shiv_ba = QRadioButton("布宜诺斯艾利斯 (Buenos Aires)")

        rb_style = "QRadioButton { font-size: 13px; spacing: 8px; padding: 3px; }"
        for rb in [self.radio_shiv_default, self.radio_shiv_mo, self.radio_shiv_kl, self.radio_shiv_dub, self.radio_shiv_ct, self.radio_shiv_ba]:
            rb.setStyleSheet(rb_style)
            self.shivering_city_group.addButton(rb)
            shivering_sub_layout.addWidget(rb)
            rb.toggled.connect(self.update_theme_state)

        self.radio_shiv_default.setChecked(True)

        scroll_layout.addWidget(self.shivering_sub_options_frame)

        scroll_layout.addWidget(self.shivering_sub_options_frame)

        scroll_layout.addWidget(self.shivering_sub_options_frame)

        # Add Separator
        bhl_sep = QFrame()
        bhl_sep.setFrameShape(QFrame.Shape.HLine)
        bhl_sep.setFrameShadow(QFrame.Shadow.Sunken)
        scroll_layout.addWidget(bhl_sep)

        # Add Black Highlighter Theme
        self.check_enable_bhl = QCheckBox("启用黑色标记笔 (Black Highlighter)")
        self.check_enable_bhl.setStyleSheet(cb_style)
        self.check_enable_bhl.toggled.connect(self.on_bhl_toggled)
        scroll_layout.addWidget(self.check_enable_bhl)

        self.bhl_sub_options_frame = QFrame()
        self.bhl_sub_options_frame.setEnabled(False)
        self.bhl_sub_options_frame.setFrameShape(QFrame.Shape.NoFrame)
        bhl_sub_layout = QVBoxLayout(self.bhl_sub_options_frame)
        bhl_sub_layout.setContentsMargins(20, 0, 0, 0)

        # BHL Sub-options
        self.check_dark_sidebar = QCheckBox("暗色侧边栏 (Dark Sidebar)") # Moved here
        self.check_bhl_collapsible = QCheckBox("可折叠侧边栏 (Collapsible Sidebar)")
        self.check_bhl_toggle = QCheckBox("切换侧边栏 (Toggle Sidebar)")
        self.check_bhl_centered = QCheckBox("居中页眉 (Centered Header)")
        self.check_bhl_office = QCheckBox("办公室 (Office)")
        self.check_bhl_raisa = QCheckBox("记录与信息安全部 (RAISA Sigma-9)")

        for cb in [self.check_dark_sidebar, self.check_bhl_collapsible, self.check_bhl_toggle, self.check_bhl_centered, self.check_bhl_office, self.check_bhl_raisa]:
            cb.setStyleSheet(cb_style)
            # We connect all to update_theme_state to refresh status/code immediately
            # Special handling for mutual exclusivity between Office and RAISA
            if cb == self.check_bhl_office:
                cb.toggled.connect(self.on_bhl_office_toggled)
            elif cb == self.check_bhl_raisa:
                cb.toggled.connect(self.on_bhl_raisa_toggled)
            else:
                cb.toggled.connect(self.update_theme_state)
            
            bhl_sub_layout.addWidget(cb)

        scroll_layout.addWidget(self.bhl_sub_options_frame)

        # Finalize Scroll Area
        scroll_area.setWidget(scroll_content)
        
        # Set max height to prevent taking up too much screen space
        scroll_area.setMaximumHeight(300) 

        basalt_vbox.addWidget(scroll_area)
        self.basalt_group.setLayout(basalt_vbox)
        comp_layout.addWidget(self.basalt_group)

        # --- AIM 配置 ---
        self.aim_group = QGroupBox("AIM 模块配置")
        self.aim_group.setVisible(False)
        aim_vbox = QVBoxLayout()
        self.aim_mode_group = QButtonGroup(self)
        self.radio_aim_full = QRadioButton("完整版头")
        self.radio_aim_top = QRadioButton("仅上半部分 (blocks=-)")
        self.radio_aim_bottom = QRadioButton("仅下半部分 (blocks=!)")

        rb_style = "QRadioButton { font-size: 13px; spacing: 8px; padding: 3px; }"
        for rb in [self.radio_aim_full, self.radio_aim_top, self.radio_aim_bottom]:
            rb.setStyleSheet(rb_style)

        self.radio_aim_full.setChecked(True)
        self.aim_mode_group.addButton(self.radio_aim_full)
        self.aim_mode_group.addButton(self.radio_aim_top)
        self.aim_mode_group.addButton(self.radio_aim_bottom)
        aim_vbox.addWidget(self.radio_aim_full)
        aim_vbox.addWidget(self.radio_aim_top)
        aim_vbox.addWidget(self.radio_aim_bottom)
        self.aim_group.setLayout(aim_vbox)
        comp_layout.addWidget(self.aim_group)

        insert_btn = QPushButton("应用/插入选定组件")
        insert_btn.setStyleSheet(
            "background-color: #f39c12; color: white; font-weight: bold; height: 50px; font-size: 16px; border-radius: 5px;")
        insert_btn.clicked.connect(self.insert_component)
        comp_layout.addWidget(insert_btn)

        export_btn = QPushButton("生成维基代码")
        export_btn.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; height: 60px; font-size: 18px; margin-top: 15px; border-radius: 6px;")
        export_btn.clicked.connect(self.export_wikidot)
        comp_layout.addWidget(export_btn)

        copy_btn = QPushButton("一键复制到剪切板")
        copy_btn.setStyleSheet(
            "background-color: #3498db; color: white; font-weight: bold; height: 40px; margin-top: 5px; border-radius: 6px; font-size: 16px;")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        comp_layout.addWidget(copy_btn)

        comp_layout.addStretch()

        source_tab = QWidget()
        source_layout = QVBoxLayout(source_tab)



        # 新增：代码导入按钮
        import_btn = QPushButton(" 识别代码并生成界面 (Render to Editor)")
        import_btn.setStyleSheet(
            "background-color: #8e44ad; color: white; font-weight: bold; height: 40px; margin-top: 5px; border-radius: 6px;")
        import_btn.clicked.connect(self.render_to_editor)
        source_layout.addWidget(import_btn)

        self.source_display = PlainPasteTextEdit()
        self.source_display.setPlaceholderText("生成的维基代码将在此显示...")
        source_layout.addWidget(self.source_display)

        left_panel.addTab(comp_tab, "编辑器")
        left_panel.addTab(source_tab, "代码视窗")

        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebPage(self.browser, self))



        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.prepare_context_menu)

        self.init_editor_html()

        splitter.addWidget(left_panel)
        splitter.addWidget(self.browser)
        splitter.setStretchFactor(1, 4)

        # --- 右侧属性面板 ---
        self.right_dock = QDockWidget("页面属性", self)
        self.right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.right_dock_content = QWidget()
        self.right_dock_layout = QVBoxLayout(self.right_dock_content)

        self.lbl_theme_status = QLabel("<b>当前版式:</b> 无")
        self.lbl_theme_status.setWordWrap(True)
        self.lbl_theme_status.setStyleSheet(
            "padding: 10px; background: #64b5f6; border: 1px solid #1976d2; border-radius: 5px; font-size: 14px;")

        self.lbl_bf_status = QLabel("<b>Better Footnotes:</b> 关闭")
        self.lbl_bf_status.setStyleSheet(
            "padding: 10px; background: #e57373; border: 1px solid #d32f2f; border-radius: 5px; margin-top: 5px; font-size: 14px;")

        self.lbl_sidebar_status = QLabel("<b>Dark Sidebar:</b> 关闭")
        self.lbl_sidebar_status.setStyleSheet(
            "padding: 10px; background: #95a5a6; border: 1px solid #7f8c8d; border-radius: 5px; margin-top: 5px; font-size: 14px; color: white;")

        self.right_dock_layout.addWidget(self.lbl_theme_status)
        self.right_dock_layout.addWidget(self.lbl_bf_status)
        self.right_dock_layout.addWidget(self.lbl_sidebar_status)
        self.right_dock_layout.addStretch()

        self.right_dock.setWidget(self.right_dock_content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

    def initiate_save(self):
        """点击保存按钮时触发"""
        self.is_saving_mode = True
        self.export_wikidot()  # 这会触发 process_html

    def init_editor_html(self):
        content = r"""
        <html>
        <head>
            <style>
                body { font-family: 'Verdana', sans-serif; padding: 40px; line-height: 1.4; background: #fff; position: relative; }
                #editor-root { min-height: 400px; outline: none; padding-bottom: 50px; }

                a { color: #b01; text-decoration: none; cursor: pointer; }
                a:hover { text-decoration: underline; }

                .rate-module-box {
                    position: absolute; top: 10px; right: 40px; 
                    background: #f0f0f0; border: 1px solid #ccc; border-radius: 4px;
                    padding: 5px; font-size: 12px; color: #333; 
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    display: flex; flex-direction: column; gap: 5px; z-index: 100;
                    user-select: none;
                }
                .rate-module-box.hidden-rate {
                    opacity: 0.5; filter: grayscale(100%);
                    text-decoration: line-through;
                }
                .rate-controls {
                    display: flex; gap: 4px; justify-content: center;
                }
                .rate-btn {
                    border: 1px solid #999; background: #fff; cursor: pointer;
                    padding: 2px 6px; border-radius: 3px; font-size: 10px;
                }
                .rate-btn:hover { background: #e0e0e0; }
                .rate-btn.active { background: #3498db; color: white; border-color: #2980b9; } 
                .rate-content {
                    font-weight: bold; padding: 2px 5px; text-align: center; border: 1px dashed #bbb; background: #fff;
                }

                .scp-component { 
                    border: 2px dashed #ccc; padding: 20px; margin: 20px 0; 
                    background: #fdfdfd; position: relative; border-radius: 8px;
                    color: #444; font-size: 14px; cursor: pointer;
                }

                /* Bounding Boxes & Tooltips */
                .scp-component:hover, .wikidot-table:hover {
                    outline: 2px solid #3498db;
                }
                .rate-module-box:hover {
                    outline: 2px solid #3498db;
                }
                
                #component-tooltip {
                    position: fixed;
                    background: rgba(0, 0, 0, 0.8);
                    color: #fff;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    pointer-events: none;
                    z-index: 10000;
                    display: none;
                }
                #footnote-preview-tooltip {
                    position: fixed;
                    background: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    padding: 8px;
                    max-width: 300px;
                    font-size: 13px;
                    z-index: 10001;
                    display: none;
                    pointer-events: none;
                    line-height: 1.4;
                }
                .scp-footnote { cursor: pointer; }
                .scp-footnote:hover { background: #e0f7fa; border-top: 2px solid #00bcd4; }


                /* Bounding Boxes & Tooltips */
                .scp-component:hover, .wikidot-table:hover {
                    outline: 2px solid #3498db;
                }
                .rate-module-box:hover {
                    outline: 2px solid #3498db;
                }
                
                #component-tooltip {
                    position: fixed;
                    background: rgba(0, 0, 0, 0.8);
                    color: #fff;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    pointer-events: none;
                    z-index: 10000;
                    display: none;
                }
                #footnote-preview-tooltip {
                    position: fixed;
                    background: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    padding: 8px;
                    max-width: 300px;
                    font-size: 13px;
                    z-index: 10001;
                    display: none;
                    pointer-events: none;
                    line-height: 1.4;
                }
                .scp-footnote { cursor: pointer; }
                .scp-footnote:hover { background: #e0f7fa; border-top: 2px solid #00bcd4; }

                /* --- AIM 渲染样式 --- */
                .aim-box {
                    border: 1px solid #ddd; background: #fff; padding: 0;
                    margin: 20px 0; font-family: 'Segoe UI', sans-serif;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05); cursor: default;
                    /* 修复：全宽显示 */
                    width: 100%; box-sizing: border-box; clear: both;
                }
                .aim-table { width: 100%; border-collapse: collapse; font-size: 13px; border: none; margin: 0; }
                .aim-table td { border: 1px solid #eee; padding: 8px 12px; vertical-align: middle; }
                .aim-label { color: #888; text-transform: uppercase; font-size: 10px; font-weight: bold; margin-bottom: 3px; }
                .aim-value { color: #333; font-weight: bold; outline: none; }
                .aim-header-title { font-size: 1.1em; font-weight: bold; color: #555; }
                .aim-footer { text-align: center; background: #f9f9f9; padding: 4px; font-size: 10px; font-weight: bold; color: #999; border-top: 2px solid #901111; }

                /* --- Image Block 样式 --- */
                .image-block-box {
                    max-width: 300px; margin: 20px auto; border: 1px solid #ccc; background: #f0f0f0; padding: 0; transition: all 0.3s;
                }
                .image-block-box[data-align="left"] { float: left; margin: 20px 20px 20px 0; }
                .image-block-box[data-align="right"] { float: right; margin: 20px 0 20px 20px; }
                .image-block-content { background: #fff; padding: 10px; text-align: center; border-bottom: 1px solid #eee; }
                .image-block-caption { padding: 10px; font-size: 0.9em; background: #f9f9f9; }
                .img-align-controls { background: #333; padding: 5px; text-align: center; display: flex; justify-content: center; gap: 5px; }
                .img-align-btn { background: #fff; border: none; font-size: 12px; cursor: pointer; padding: 2px 8px; border-radius: 3px; }
                .img-align-btn:hover { background: #ddd; }
                .img-toggle-btn { position: absolute; top: 0; right: 0; width: 24px; height: 24px; background: #fff; border: 1px solid #aaa; font-size: 14px; cursor: pointer; z-index: 10; opacity: 0.7; }
                .img-toggle-btn:hover { opacity: 1; }
                .img-controls-hidden .img-controls-wrapper { display: none; }

                [data-field="name"] {
                    word-break: break-all;
                    min-width: 50px; 
                    display: inline-block; 
                    border-bottom: 1px dashed #ccc;
                }

                /* --- Table 样式 (修复) --- */
                table.wikidot-table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                    font-size: 14px;
                    border: 1px solid #333; /* 显式边框颜色 */
                }
                table.wikidot-table th, table.wikidot-table td {
                    border: 1px solid #333; /* 单元格显式边框 */
                    padding: 8px;
                    min-width: 30px;
                    vertical-align: top;
                }
                table.wikidot-table th {
                    background-color: #f4f4f4;
                    font-weight: bold;
                    text-align: center;
                }
                table.wikidot-table.no-border, table.wikidot-table.no-border th, table.wikidot-table.no-border td {
                    border: 1px dashed #ccc !important; /* 虚线提示 */
                }

                /* --- Tab View 样式 --- */
                .tabview-box { border: 1px solid #ccc; background: #fff; display: flex; flex-direction: column; overflow: hidden; clear: both; }
                .tab-header { display: flex; background: #f4f4f4; border-bottom: 1px solid #ccc; gap: 2px; padding: 5px 5px 0 5px; }
                .tab-btn { 
                    padding: 8px 15px; cursor: pointer; border: 1px solid #ccc; border-bottom: none; 
                    background: #e8e8e8; border-radius: 4px 4px 0 0; font-size: 13px; font-weight: bold; color: #666;
                    outline: none;
                }
                .tab-btn:hover { background: #f0f0f0; }
                .tab-btn.active { background: #fff; border-bottom: 1px solid #fff; margin-bottom: -1px; color: #333; }
                .tab-add { padding: 8px 12px; cursor: pointer; color: #888; font-weight: bold; }
                .tab-contents { padding: 15px; border-top: 1px solid #eee; min-height: 50px; }
                .tab-item { display: none; }
                .tab-item.active { display: block; }

                /* --- User Component 样式 --- */
                .user-tag { 
                    background: #f0f0f0; padding: 2px 6px; border-radius: 3px; border: 1px solid #ddd; 
                    display: inline-flex; align-items: center; gap: 4px; font-size: 12px;
                }
                .user-icon { width: 12px; height: 12px; background: #b01; border-radius: 2px; }

                /* --- 标题样式 --- */
                h1, h2, h3, h4, h5, h6 { color: #901111; margin-top: 1.5em; margin-bottom: 0.5em; font-weight: bold; }
                h1 { border-bottom: 2px solid #901111; font-size: 1.8em; }
                h2 { border-bottom: 1px solid #ccc; font-size: 1.6em; }

                /* --- 引用块样式 --- */
                blockquote {
                    border-left: 5px solid #ccc; margin: 1.5em 10px; padding: 0.5em 10px; background-color: #f9f9f9; color: #555;
                }

                /* --- 折叠块增强样式 --- */
                .collapsible-box { border: 1px solid #aaa; background: #f9f9f9; padding: 0; margin: 15px 0; border-radius: 4px; overflow: hidden; width: 100%; box-sizing: border-box; clear: both; }
                .collapsible-header { display: flex; gap: 15px; background: #e0e0e0; padding: 8px 15px; font-size: 12px; color: #333; cursor: pointer; align-items: center; border-bottom: 1px solid #ccc; }
                .title-label { font-weight: bold; color: #901111; }
                .title-input { border-bottom: 1px dashed #666; padding: 0 5px; outline: none; min-width: 60px; color: #000; background: #fff; }
                .collapsible-content-area { padding: 15px; background: #fff; min-height: 40px; cursor: text; display: none; }
                .collapsible-box.open .collapsible-content-area { display: block; }

                /* --- 授权引用修复样式 --- */
                .license-box { border: 1px solid #901111; padding: 0; background: #fff; font-size: 13px; color: #333; overflow: hidden; width: 100%; box-sizing: border-box; clear: both; }
                .license-header { color: #901111; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: space-between; padding: 8px 15px; background: #fdfdfd; }
                .license-header::after { content: '▼'; font-size: 10px; margin-left: 10px; }
                .license-box.open .license-header::after { content: '▲'; }
                .license-content { display: none; padding: 15px; line-height: 1.8; }
                .license-box.open .license-content { display: block; }
                .license-field-row { margin-bottom: 4px; border-bottom: 1px dotted #eee; display: flex; align-items: baseline; }
                .license-link-row { flex-direction: column; align-items: flex-start; }
                .license-link-row .editable-field { width: 100%; word-break: break-all; margin-top: 2px; }
                .field-label { font-weight: bold; color: #666; width: 80px; flex-shrink: 0; }
                .editable-field { border-bottom: 1px dashed #ccc; flex-grow: 1; min-width: 0; color: #333; word-break: break-all; white-space: pre-wrap; }
                .editable-field:empty::before { content: " (点击输入) "; color: #ccc; font-weight: normal; font-style: italic; }
                .editable-field:focus { border-bottom: 1px solid #000; outline: none; background: #e8f0fe; }
                .extra-files-container { border-top: 2px dashed #901111; margin-top: 10px; padding-top: 10px; }
                .file-entry { border: 1px solid #ccc; background: #f9f9f9; padding: 10px; margin-bottom: 10px; border-radius: 4px; position: relative; }
                .btn-add-file { background: #901111; color: white; border: none; padding: 8px 16px; cursor: pointer; font-size: 14px; margin-top: 5px; border-radius: 4px; }
                .btn-del-file { position: absolute; top: 2px; right: 5px; color: red; cursor: pointer; font-weight: bold; border: none; background: none; font-size: 20px; }

                /* ACS 样式 */
                .acs-box { border-left: 12px solid var(--acs-color, #f1c40f); text-align: left; background: #f9f9f9; padding: 15px 20px; display: flex; flex-direction: column; gap: 8px; font-family: 'Segoe UI', sans-serif; transition: all 0.3s ease; clear: both; }
                .acs-header-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                .acs-title { font-weight: bold; font-size: 1.1em; color: #333; }
                .acs-item-num { font-family: monospace; font-size: 1.1em; color: #901111; font-weight: bold; }
                .acs-anim-toggle { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #666; }
                .switch { position: relative; display: inline-block; width: 30px; height: 16px; }
                .switch input { opacity: 0; width: 0; height: 0; }
                .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 16px; }
                .slider:before { position: absolute; content: ""; height: 12px; width: 12px; left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%; }
                input:checked + .slider { background-color: #27ae60; }
                input:checked + .slider:before { transform: translateX(14px); }

                .scp-footnote { color: #B22222 !important; font-weight: bold; vertical-align: super; font-size: 0.8em; cursor: pointer; user-select: none; margin: 0 1px; padding: 0 1px; }
                #footnote-list-footer { margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; font-size: 0.9em; color: #555; }
                .footnote-list-item { margin-bottom: 5px; }
                .footnote-content { outline: none; border-bottom: 1px dashed transparent; }
                .footnote-content:focus { border-bottom: 1px dashed #999; background: #fffdf0; }

                .scp-hr { height: 40px; border: 1px dashed transparent; display: flex; align-items: center; justify-content: center; position: relative; }
                .scp-hr::after { content: ""; width: 100%; height: 2px; background: #333; display: block; }
                .scp-hr:hover { border: 1px dashed #901111; background: rgba(144, 17, 17, 0.05); }

                .size-span { display: inline; }
                
                /* New: Return Symbol */
                /* DIV Module */
                .div-box { border: 1px dashed #bbb; margin: 10px 0; padding: 5px; background: #f9f9f9; position: relative; clear: both; }
                .div-header { font-size: 0.8em; color: #666; border-bottom: 1px solid #ddd; margin-bottom: 5px; padding-bottom: 2px; }
                .div-content { min-height: 20px; }

                /* CSS Module */
                .css-box { border: 1px solid #a0a0a0; margin: 10px 0; background: #f0f0f0; position: relative; clear: both; }
                .css-header { background: #e0e0e0; font-size: 0.8em; padding: 2px 5px; font-weight: bold; color: #333; border-bottom: 1px solid #ccc; }
                .css-content { padding: 5px; font-family: monospace; white-space: pre-wrap; min-height: 20px; color: #222; }
                .css-hint { font-size: 0.75em; color: #666; padding: 2px 5px; background: #e8e8e8; border-top: 1px solid #ccc; font-style: italic; user-select: none; pointer-events: none; }
            </style>
            <script>
                const COLOR_MAP = {
                    'safe': '#27ae60', 
                    'euclid': '#f1c40f', 
                    'keter': '#c0392b',
                    'neutralized': '#7f8c8d', // Gray
                    'pending': '#bdc3c7',     // Light Gray
                    'explained': '#95a5a6',   // Gray
                    'esoteric': '#595959'     // Dark Gray
                };

                const ACS_ICON_MAP = {
                    'apollyon': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/apollyon-icon.svg',
                    'archon': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/archon-icon.svg',
                    'hiemal': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/hiemal-icon.svg',
                    'tiamat': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/tiamat-icon.svg',
                    'ticonderoga': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/ticonderoga-icon.svg',
                    'thaumiel': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/thaumiel-icon.svg'
                };

                function toggleMonospace() {
                    document.execCommand('styleWithCSS', false, true);
                    const fontName = document.queryCommandValue('fontName');
                    if (fontName.includes('Courier') || fontName.includes('monospace')) {
                        document.execCommand('fontName', false, 'Verdana');
                    } else {
                        document.execCommand('fontName', false, 'Courier New');
                    }
                }

                function setImgAlign(btn, align) {
                    const box = btn.closest('.image-block-box');
                    if (box) {
                        box.setAttribute('data-align', align);
                    }
                }

                function rateAction(action, btn) {
                    const box = btn.closest('.rate-module-box');
                    if (action === 'hide') {
                        if (box.classList.contains('hidden-rate')) {
                            box.classList.remove('hidden-rate');
                            box.setAttribute('data-hidden', 'false');
                            btn.innerText = '隐藏';
                        } else {
                            box.classList.add('hidden-rate');
                            box.setAttribute('data-hidden', 'true');
                            btn.innerText = '恢复';
                        }
                    } else if (action === 'left' || action === 'right') {
                        // Toggle logic: if already active, clear it? Or just switch.
                        // User request: "left, right ... click to cancel". 
                        // Actually prompt said: "Hide... click to cancel rendering... click again to restore". 
                        // For alignment: "left... right...".
                        // Let's implement radio-like behavior for alignment.
                        
                        const currentAlign = box.getAttribute('data-align');
                        if (currentAlign === action) {
                             box.removeAttribute('data-align');
                             btn.classList.remove('active');
                        } else {
                             box.setAttribute('data-align', action);
                             box.querySelectorAll('.rate-align-btn').forEach(b => b.classList.remove('active'));
                             btn.classList.add('active');
                        }
                    }
                }

                function toggleImgControls(btn) {
                    const box = btn.closest('.image-block-box');
                    box.classList.toggle('img-controls-hidden');
                }

                // Paste handler for cleaning links
                document.addEventListener('paste', function(e) {
                    const target = e.target;
                    // Check for image link field OR secondary icon field
                    if (target.matches('.image-block-box [data-field="name"]') || 
                        target.closest('.image-block-box [data-field="name"]') ||
                        target.matches('.acs-box [data-field="secondary-icon"]') ||
                        target.closest('.acs-box [data-field="secondary-icon"]')) {

                        e.preventDefault();
                        const text = (e.clipboardData || window.clipboardData).getData('text/plain');
                        document.execCommand('insertText', false, text);
                    }
                });

                function refreshImg(span) {
                    const box = span.closest('.image-block-box');
                    const img = box.querySelector('.img-preview');
                    const placeholder = box.querySelector('.img-placeholder');
                    const nameField = box.querySelector('[data-field="name"]');
                    const url = nameField ? nameField.innerText.trim() : '';

                    if (url && (url.startsWith('http') || url.startsWith('//'))) {
                        img.src = url;
                        img.style.display = 'block';
                        placeholder.style.display = 'none';
                        img.onerror = function() {
                            img.style.display = 'none';
                            placeholder.style.display = 'block';
                            placeholder.innerText = '[无效的图片链接]';
                        }
                    } else {
                        img.style.display = 'none';
                        placeholder.style.display = 'block';
                        placeholder.innerText = '[图片预览区域]';
                    }

                    const wSpan = box.querySelector('[data-field="width"]');
                    const hSpan = box.querySelector('[data-field="height"]');

                    if (wSpan) {
                        let w = wSpan.innerText.trim();
                        if (w && !isNaN(w)) w += "px";
                        img.style.width = w;
                    }

                    if (hSpan) {
                        let h = hSpan.innerText.trim();
                        if (h && !isNaN(h)) h += "px";
                        img.style.height = h;
                    }
                }

                function selectTab(btn) {
                    const header = btn.parentElement;
                    const box = header.parentElement;
                    const index = Array.from(header.children).indexOf(btn);

                    Array.from(header.querySelectorAll('.tab-btn')).forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    const contents = box.querySelector('.tab-contents');
                    Array.from(contents.children).forEach((c, i) => {
                        c.classList.toggle('active', i === index);
                    });
                }

                function addTab(btn) {
                    const header = btn.parentElement;
                    const box = header.parentElement;
                    const contents = box.querySelector('.tab-contents');
                    const newBtn = document.createElement('span');
                    newBtn.className = 'tab-btn';
                    newBtn.setAttribute('contenteditable', 'true');
                    newBtn.onclick = function() { selectTab(this); };
                    newBtn.innerText = 'New Tab';
                    header.insertBefore(newBtn, btn);
                    const newContent = document.createElement('div');
                    newContent.className = 'tab-item';
                    newContent.setAttribute('contenteditable', 'true');
                    newContent.innerHTML = '<p>Tab Content...</p>';
                    contents.appendChild(newContent);
                    selectTab(newBtn);
                }

                function removeTab(btn) {
                    const header = btn.parentElement;
                    const box = header.closest('.tabview-box');
                    const index = Array.from(header.children).indexOf(btn);
                    const contents = box.querySelector('.tab-contents');
                    if (header.querySelectorAll('.tab-btn').length <= 1) {
                         alert('至少保留一个选项卡');
                         return;
                    }
                    btn.remove();
                    if (contents.children[index]) contents.children[index].remove();
                    const firstBtn = header.querySelector('.tab-btn');
                    if (firstBtn) selectTab(firstBtn);
                }

                function insertTable() {
                    const html = `
                    <table border="1" class="wikidot-table">
                        <tr><th contenteditable="true">~ 标题 1</th><th contenteditable="true">~ 标题 2</th><th contenteditable="true">~ 标题 3</th></tr>
                        <tr><td contenteditable="true">内容 1</td><td contenteditable="true">内容 2</td><td contenteditable="true">内容 3</td></tr>
                        <tr><td contenteditable="true">内容 4</td><td contenteditable="true">内容 5</td><td contenteditable="true">内容 6</td></tr>
                    </table><p><br></p>`;
                    document.execCommand('insertHTML', false, html);
                }

                function insertLicenseBox() {
                    var editor = document.getElementById('editor-root');
                    var html = '<div class="scp-component license-box open" data-type="license" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)</div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true"></span></div><hr><div class="extra-files-container"></div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>';
                    editor.insertAdjacentHTML('beforeend', html);
                }

                function tableAction(action) {
                    const sel = window.getSelection();
                    if (!sel.rangeCount) return;
                    const cell = sel.anchorNode.nodeType === 3 ? sel.anchorNode.parentElement.closest('td, th') : sel.anchorNode.closest('td, th');
                    if (!cell) return;
                    const row = cell.parentElement;
                    const table = row.parentElement.closest('table');
                    const rows = Array.from(table.rows);
                    const rowIndex = row.rowIndex;
                    const colIndex = cell.cellIndex;

                    if (action === 'addRow') {
                        const newRow = table.insertRow(rowIndex + 1);
                        for (let i = 0; i < row.cells.length; i++) {
                            const newCell = newRow.insertCell(i);
                            newCell.innerText = '内容';
                            newCell.setAttribute('contenteditable', 'true');
                        }
                    } else if (action === 'delRow') {
                        table.deleteRow(rowIndex);
                        if (table.rows.length === 0) table.remove();
                    } else if (action === 'addCol') {
                        for (let i = 0; i < rows.length; i++) {
                            const newCell = rows[i].insertCell(colIndex + 1);
                            newCell.innerText = '内容';
                            newCell.setAttribute('contenteditable', 'true');
                            if (rows[i].cells[colIndex].tagName === 'TH') {
                                // Keep header styling if originally a header column, simplistic approach
                            }
                        }
                    } else if (action === 'delCol') {
                        for (let i = 0; i < rows.length; i++) {
                            if (rows[i].cells.length > colIndex) {
                                rows[i].deleteCell(colIndex);
                            }
                        }
                        if (table.rows[0] && table.rows[0].cells.length === 0) table.remove();
                    } else if (action === 'delTable') {
                        table.remove();
                    } else if (action === 'mergeRight') {
                        if (colIndex < row.cells.length - 1) {
                            const nextCell = row.cells[colIndex + 1];
                            const currentColSpan = parseInt(cell.getAttribute('colspan') || 1);
                            const nextColSpan = parseInt(nextCell.getAttribute('colspan') || 1);
                            cell.setAttribute('colspan', currentColSpan + nextColSpan);
                            if(nextCell.innerText.trim()) cell.innerHTML += ' ' + nextCell.innerHTML;
                            row.deleteCell(colIndex + 1);
                        }
                    } else if (action === 'toggleBorder') {
                        if (table.classList.contains('no-border')) {
                             table.classList.remove('no-border');
                             table.setAttribute('border', '1');
                        } else {
                             table.classList.add('no-border');
                             table.setAttribute('border', '0');
                        }
                    }
                }

                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Backspace') {
                        const sel = window.getSelection();
                        if (!sel.rangeCount || !sel.isCollapsed) return;

                        // Smart Backspace: Delete empty line between Component and Body Text
                        const smartNode = sel.anchorNode;
                        const smartBlock = smartNode.nodeType === 3 ? smartNode.parentElement : smartNode;
                        
                        if (smartBlock && (smartBlock.tagName === 'P' || smartBlock.tagName === 'DIV') && smartBlock.innerText.replace(/\n/g, '').trim() === '') {
                             const prev = smartBlock.previousElementSibling;
                             const next = smartBlock.nextElementSibling;
                             if (prev && next) {
                                 // Refined: Exclude Image Blocks (.image-block-box)
                                 const isComp = prev.matches && prev.matches('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box');
                                 const isImage = prev.matches && prev.matches('.image-block-box');
                                 
                                 // Check if next is body text (has content)
                                 const hasContent = next.innerText && next.innerText.trim().length > 0;
                                 
                                 if (isComp && !isImage && hasContent) {
                                     e.preventDefault();
                                     smartBlock.remove();
                                     const newR = document.createRange();
                                     // Refined: set cursor AFTER the previous component (visually to its right/end)
                                     if (prev) newR.setStartAfter(prev);
                                     newR.collapse(true);
                                     sel.removeAllRanges();
                                     sel.addRange(newR);
                                     return;
                                 }
                             }
                        }
                        
                        // Fix: Prevent cursor disappearing when backspacing against a component
                        const range = sel.getRangeAt(0);
                        if (range.startOffset === 0) {
                            let node = range.startContainer;
                            if (node.nodeType === 3) {
                                if (node.previousSibling && node.previousSibling.nodeType === 1 && node.previousSibling.classList.contains('scp-component')) {
                                    e.preventDefault(); return;
                                }
                                if (!node.previousSibling) node = node.parentNode;
                            }
                            if (node.nodeType === 1 && node.previousElementSibling && node.previousElementSibling.classList.contains('scp-component')) {
                                e.preventDefault(); return;
                            }
                        }

                        const anchor = sel.anchorNode;
                        const element = anchor.nodeType === 3 ? anchor.parentElement : anchor;
                        const blockquote = element.closest('blockquote');
                        if (blockquote) {
                            const range = document.createRange();
                            range.selectNodeContents(blockquote);
                            range.setEnd(sel.anchorNode, sel.anchorOffset);
                            if (range.toString().trim() === '') {
                                document.execCommand('formatBlock', false, 'p');
                            }
                        }
                        const li = element.closest('li');
                        if (li) {
                            if (li.textContent.trim() === '') {
                                document.execCommand('outdent');
                                if (li.closest('ul, ol') && li.parentElement.children.length === 1) {
                                     document.execCommand('formatBlock', false, 'p');
                                }
                            }
                        }
                    }
                });

                function updateTerminalStyle() {
                    // Map DIV classes from Header to Box for Live Preview
                    var divBoxes = document.querySelectorAll('.div-box');
                    divBoxes.forEach(function(box) {
                         var header = box.querySelector('.div-header');
                         if (header) {
                             var text = header.textContent || ""; // Use textContent for robustness
                             // STRICT PARSING: Only check the first line (same line as DIV:...)
                             var firstLine = text.split('\n')[0];
                             // Ensure we are matching `class="..."` specifically
                             var match = firstLine.match(/class="([^"]+)"/);
                             if (match) {
                                 var clsList = match[1].split(' ');
                                 clsList.forEach(function(c) { if(c) box.classList.add(c); });
                             }
                         }
                    });
                   
                    var hasTerminal = false;
                    var hasTerminal001 = false;
                    var cssModules = document.querySelectorAll('.css-box .css-content');
                    var allCss = "";
                    
                    cssModules.forEach(function(mod) {
                        var text = mod.textContent; // FIX: Use textContent to read hidden/collapsed CSS
                        allCss += text + "\n";
                        if (text.indexOf('.danke') !== -1 && text.indexOf('.agent') !== -1) {
                            hasTerminal = true;
                        }
                        // Revert to looser detection to ensure it catches existing modules
                        if (text.indexOf('div.terminal') !== -1 || text.indexOf('.terminal') !== -1) {
                            hasTerminal001 = true;
                        }
                    });

                    // PERMANENT RENDERING FIX:
                    // If Terminal #001 CSS exists, FIND all div-boxes that look like Terminal #001 (contain scanline)
                    // and FORCE the 'terminal' class on them.
                    if (hasTerminal001) {
                        divBoxes.forEach(function(box) {
                             // Check for scanline child (Unique feature of Terminal #001)
                             // Scanline is a nested div-box with "scanline" in its header
                             var headers = box.querySelectorAll('.div-header');
                             var isTerminal = false;
                             for (var i=0; i<headers.length; i++) {
                                 // Use textContent here as well
                                 if (headers[i].textContent.indexOf('scanline') !== -1) {
                                     isTerminal = true; 
                                     break;
                                 }
                             }
                             
                             if (isTerminal) {
                                 if (!box.classList.contains('terminal')) {
                                     box.classList.add('terminal');
                                 }
                             }
                        });
                    }

                    var styleId = 'dynamic-terminal-style';
                    var style = document.getElementById(styleId);

                    // Build extra CSS
                    var extraInfo = "";
                    
                    if (hasTerminal) {
                        extraInfo += `
                        /* Force Terminal Style for all DIV modules in Editor View */
                        .div-box {
                            background-color: #000000 !important;
                            border: 2px solid #55AA55 !important;
                            color: #77CC77 !important;
                            font-family: monospace !important;
                        }
                        .div-header {
                            background-color: #55AA55 !important;
                            color: #002200 !important;
                            border-bottom: 1px solid #002200 !important;
                            font-weight: bold;
                        }
                        .div-content {
                            background-color: #000000 !important;
                            color: #77CC77 !important;
                        }
                        `;
                    }
                    
                    if (hasTerminal001) {
                         extraInfo += `
                         /* Fix for Terminal #001 Nested Divs */
                         .div-box.terminal .div-box {
                             background-color: #000000 !important;
                             border: 1px dashed #333 !important; 
                             box-shadow: none !important; 
                         }
                         /* Nested Content Black */
                         .div-box.terminal .div-box .div-content {
                             background-color: #000000 !important;
                             color: #77CC77 !important;
                         }
                         /* Nested Headers - HIDE for Clean Preview */
                         .div-box.terminal .div-box .div-header {
                             display: none !important;
                         }

                         /* FORCE ALL DESCENDANTS BLACK BACKGROUND (except special text) */
                         .div-box.terminal * {
                             background-color: transparent; /* Default to transp so parent black shows, avoids white patches */
                         }
                         .div-box.terminal .div-content {
                             background-color: #000000 !important; /* Ensure main container is black */
                         }
                         .div-box.terminal blockquote,
                         .div-box.terminal blockquote * {
                             background-color: #000000 !important;
                             color: #77CC77 !important;
                             border-color: #77CC77 !important; /* Ensure border color matches */
                         }
                         .div-box.terminal blockquote {
                             border: 3px double #77CC77 !important;
                         }

                         /* EXCEPTION: Scanline - HIDDEN in Editor View */
                         .div-box.terminal .div-box.scanline {
                             display: none !important;
                         }

                         /* Fix for OUTER Terminal .div-box */
                         .div-box.terminal {
                             background-color: #000000 !important;
                             border: 3px solid #BBBBBB !important;
                             border-radius: 16px !important;
                             box-shadow: inset 0 0 10em 1em rgba(0,0,0,0.5) !important;
                         }
                         /* Outer Content Transparent */
                         .div-box.terminal > .div-content {
                             background-color: transparent !important;
                             color: #77CC77 !important;
                             padding: 2px !important;
                         }
                         /* Outer Header - HIDE for Clean Preview */
                         .div-box.terminal > .div-header {
                              display: none !important;
                         }
                         `;
                    }

                    if (allCss.trim()) {
                         if (!style) {
                            style = document.createElement('style');
                            style.id = styleId;
                            document.head.appendChild(style);
                        }
                        style.textContent = allCss + extraInfo;
                    } else if (style) {
                        style.textContent = "";
                    }
                }

                function setupObserver() {
                    const editor = document.getElementById('editor-root');
                    if(!editor) return; // Guard
                    const observer = new MutationObserver((mutations) => {
                        let needsRefresh = false;
                        let contentChanged = false;
                        
                        mutations.forEach((mutation) => {
                            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                                needsRefresh = true;
                                contentChanged = true;
                            }
                        });
                        
                        if (contentChanged) {
                             try {
                                 handleTitleMarkdown();
                             } catch (e) {
                                 console.error("Markdown Error: ", e);
                             }
                             try {
                                 updateTerminalStyle(); // Check for CSS updates live
                             } catch (e) {
                                 console.error("Style Update Error: ", e);
                             }
                        }
                        
                        if (needsRefresh && !document.activeElement.closest('#footnote-list-footer')) {
                            try {
                                refreshFootnotes();
                            } catch (e) {
                                console.error("Footnote Error: ", e);
                            }
                        }
                    });
                    observer.observe(editor, { childList: true, characterData: true, subtree: true });
                    // Initial check
                    updateTerminalStyle();
                }

                function handleTitleMarkdown() {
                    const sel = window.getSelection();
                    if (!sel.rangeCount) return;
                    const range = sel.getRangeAt(0);
                    let node = range.startContainer;
                    let block = node;
                    while (block && block.parentNode && block.parentNode.id !== 'editor-root') block = block.parentNode;
                    if (block && block.nodeType === 1 && block.id !== 'editor-root') {
                        const text = block.innerText;
                        // Avoid unnecessary regex matches on empty lines or non-title lines
                        if (!text || !text.startsWith('+')) return;
                        
                        const match = text.match(new RegExp("^([+]{1,6})\\\\s+(.*)"));
                        if (match) {
                            const level = match[1].length;
                            const content = match[2];
                            const hTag = 'H' + level;
                            if (block.tagName !== hTag) {
                                const newH = document.createElement(hTag);
                                newH.innerText = content;
                                block.parentNode.replaceChild(newH, block);
                                const newRange = document.createRange();
                                newRange.selectNodeContents(newH);
                                newRange.collapse(false);
                                sel.removeAllRanges();
                                sel.addRange(newRange);
                            }
                        }
                    }
                }


                function refreshFootnotes() {
                    if (document.activeElement && document.activeElement.closest('#footnote-list-footer')) return;
                    const editor = document.getElementById('editor-root');
                    const footer = document.getElementById('footnote-list-footer');
                    const footnotes = editor.querySelectorAll('.scp-footnote');
                    if (footnotes.length === 0) { footer.innerHTML = ""; return; }
                    let html = "<b>脚注预览 (可编辑):</b><br>";
                    footnotes.forEach((fn, index) => {
                        const num = index + 1;
                        if (fn.innerText != num) fn.innerText = num;
                        const content = fn.getAttribute('data-content') || '待输入';
                        html += `<div class="footnote-list-item"><span style="color:#B22222;font-weight:bold;">${num}.</span> <span class="footnote-content" contenteditable="true" oninput="updateFootnoteFromPreview(${index}, this)">${content}</span></div>`;
                    });
                    if (footer.innerHTML !== html) footer.innerHTML = html;
                }

                function updateFootnoteFromPreview(index, el) {
                    const editor = document.getElementById('editor-root');
                    const footnotes = editor.querySelectorAll('.scp-footnote');
                    if (footnotes[index]) {
                         const txt = el.innerText;
                         footnotes[index].setAttribute('data-content', txt);
                         footnotes[index].setAttribute('title', txt);
                    }
                }

                function editLicenseLink(el) {
                    // Ensure element has an ID for targeting
                    if (!el.id) {
                        el.id = 'license-link-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
                    }
                    window.location.href = "edit-license-link://" + el.id;
                }

                function applyFontSize(sizeValue) {
                    const sel = window.getSelection();
                    if (!sel.rangeCount || sel.isCollapsed) return;
                    const range = sel.getRangeAt(0);
                    let targetNode = range.commonAncestorContainer;
                    if (targetNode.nodeType === 3) targetNode = targetNode.parentNode;
                    if (targetNode.classList.contains('size-span') && targetNode.innerText === sel.toString()) {
                        targetNode.style.fontSize = sizeValue;
                        const newRange = document.createRange();
                        newRange.selectNodeContents(targetNode);
                        sel.removeAllRanges(); sel.addRange(newRange);
                    } else {
                        const span = document.createElement('span');
                        span.className = 'size-span';
                        span.style.fontSize = sizeValue;
                        try {
                            const content = range.extractContents();
                            span.appendChild(content);
                            range.insertNode(span);
                            const newRange = document.createRange();
                            newRange.selectNodeContents(span);
                            sel.removeAllRanges(); sel.addRange(newRange);
                        } catch (e) { console.error(e); }
                    }
                }

                function applyAcsChange(element, className) {
                    const acsBox = element.closest('.acs-box');
                    if (!acsBox) return;
                    const val = className.toLowerCase();
                    if (COLOR_MAP[val]) {
                        acsBox.style.setProperty('--acs-color', COLOR_MAP[val]);
                        acsBox.setAttribute('data-container', val);
                        const label = acsBox.querySelector('[data-field="container"]');
                        if (label) label.innerText = className;
                        
                        // Auto-cleanup Secondary if not Esoteric
                        if (val !== 'esoteric') {
                            const secLabel = acsBox.querySelector('[data-field="secondary"]');
                            const iconLabel = acsBox.querySelector('[data-field="secondary-icon"]');
                            if (secLabel && secLabel.innerText.toLowerCase() !== 'none') {
                                secLabel.innerText = 'none';
                                if (iconLabel) iconLabel.innerText = '';
                                // Update internal state/styles if needed, though secondary styling is minimal
                            }
                        }
                    }
                }

                function applyAcsSecondary(element, className) {
                    const acsBox = element.closest('.acs-box');
                    if (!acsBox) return;
                    const label = acsBox.querySelector('[data-field="secondary"]');
                    if (label) label.innerText = className;
                    
                    const val = className.toLowerCase();
                    
                    // Auto-fill Icon
                    const iconLabel = acsBox.querySelector('[data-field="secondary-icon"]');
                    if (iconLabel) {
                        if (ACS_ICON_MAP[val]) {
                            iconLabel.innerText = ACS_ICON_MAP[val];
                        } else if (val === 'none') {
                            iconLabel.innerText = '';
                        }
                    }

                    // Auto switch to esoteric if secondary is present
                    if (className.toLowerCase() !== 'none') {
                        const containerLabel = acsBox.querySelector('[data-field="container"]');
                        if (containerLabel) {
                            containerLabel.innerText = 'Esoteric';
                            applyAcsChange(containerLabel, 'Esoteric');
                        }
                    }
                }

                function addLicenseFile(btn) {
                    const container = btn.previousElementSibling;
                    const div = document.createElement('div');
                    div.className = 'file-entry';
                    div.innerHTML = `<button class="btn-del-file" onclick="this.parentElement.remove()">×</button><div class="license-field-row"><span class="field-label">文件名：</span><span class="editable-field" data-field="file_name" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">图像名：</span><span class="editable-field" data-field="img_name" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">图像作者：</span><span class="editable-field" data-field="img_author" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">授权协议：</span><span class="editable-field" data-field="img_license" contenteditable="true"></span></div><div class="license-field-row license-link-row"><span class="field-label">来源链接：</span><span class="editable-field" data-field="source_link" contenteditable="false" onclick="editLicenseLink(this)"></span></div><div class="license-field-row"><span class="field-label">衍生自：</span><span class="editable-field" data-field="derived_from" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">备注：</span><span class="editable-field" data-field="note" contenteditable="true"></span></div>`;
                    container.appendChild(div);
                }

                document.addEventListener('click', function(e) {
                    const licHeader = e.target.closest('.license-header');
                    if (licHeader) { licHeader.parentElement.classList.toggle('open'); return; }
                    const colHeader = e.target.closest('.collapsible-header');
                    if (colHeader && !e.target.closest('.title-input')) { colHeader.parentElement.classList.toggle('open'); }

                    // Click-to-Insert-Newline on Right Side
                    const comp = e.target.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box');
                    if (comp && !comp.matches('.image-block-box')) {
                        // Prevent triggering on interactive elements or headers
                        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT' || e.target.tagName === 'A' || 
                            e.target.closest('.rate-controls') || e.target.closest('.license-header') || e.target.closest('.collapsible-header') || e.target.closest('.tab-header')) {
                            return;
                        }

                        const rect = comp.getBoundingClientRect();
                        const isRightSide = (e.clientX >= rect.right - Math.max(30, rect.width * 0.1)); // Right 10% or 30px
                        
                        if (isRightSide) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            // Check if next sibling is empty line
                            let next = comp.nextElementSibling;
                            if (!next || (next.tagName !== 'P' && next.tagName !== 'DIV') || next.innerText.trim() !== '') {
                                const p = document.createElement('p');
                                p.innerHTML = '<br>';
                                comp.parentNode.insertBefore(p, next);
                                next = p;
                            }
                            
                            // Move cursor to the next line
                            const range = document.createRange();
                            range.selectNodeContents(next);
                            range.collapse(true);
                            const sel = window.getSelection();
                            sel.removeAllRanges();
                            sel.addRange(range);
                        }
                    }
                });

                document.addEventListener('input', function(e) {
                    // ACS Live Update
                    const acsContainer = e.target.closest('[data-field="container"]');
                    if (acsContainer && acsContainer.closest('.acs-box')) {
                        const val = acsContainer.innerText.trim();
                        applyAcsChange(acsContainer, val);
                    }
                    // Setup tooltips logic if not exists (lazy init or just init in onload)
                });

                let tooltip = null;
                let fnTooltip = null;

                function setupTooltips() {
                    tooltip = document.createElement('div');
                    tooltip.id = 'component-tooltip';
                    document.body.appendChild(tooltip);

                    fnTooltip = document.createElement('div');
                    fnTooltip.id = 'footnote-preview-tooltip';
                    document.body.appendChild(fnTooltip);

                    document.addEventListener('mouseover', (e) => {
                        // Component Tooltip
                         const comp = e.target.closest('.scp-component, .wikidot-table');
                         const isFooter = e.target.closest('#footnote-list-footer');
                         
                         if (comp && !isFooter) {
                             let type = comp.getAttribute('data-type') || 'Unknown Component';
                             if (comp.classList.contains('wikidot-table')) type = "Table";
                             if (comp.classList.contains('rate-module-box')) type = "Rate Module";
                             // Specific names
                             if (type === 'acs') type = "ACS Component";
                             if (type === 'image-block') type = "Image Block";
                             if (type === 'image-block-adv') type = "Adv Image";
                             if (type === 'tabview') type = "Tab View";
                             if (type === 'collapsible') type = "Collapsible";
                             
                             if (type !== 'footnote') {
                                 tooltip.innerText = type;
                                 tooltip.style.display = 'block';
                                 
                                 // Position logic
                                 const rect = comp.getBoundingClientRect();
                                 tooltip.style.left = rect.left + 'px';
                                 tooltip.style.top = (rect.top - 25) + 'px';
                             } else {
                                 tooltip.style.display = 'none';
                             }
                         } else {

                             tooltip.style.display = 'none';
                         }

                         // Footnote Hover
                         const fn = e.target.closest('.scp-footnote');
                         if (fn) {
                             const content = fn.getAttribute('data-content') || '无内容';
                             fnTooltip.innerText = content;
                             fnTooltip.style.display = 'block';
                             
                             const rect = fn.getBoundingClientRect();
                             fnTooltip.style.left = (rect.left + 20) + 'px';
                             fnTooltip.style.top = (rect.top + 20) + 'px';
                         } else {
                             fnTooltip.style.display = 'none';
                         }
                    });
                    
                    document.addEventListener('mouseout', (e) => {
                         // Simple hide on mouseout of window/body? 
                         // Check relatedTarget
                         if (!e.relatedTarget) {
                             tooltip.style.display = 'none';
                             fnTooltip.style.display = 'none';
                         }
                    });

                    document.addEventListener('click', (e) => {
                        const fn = e.target.closest('.scp-footnote');
                        if (fn) {
                            // Find index
                            const allFn = Array.from(document.querySelectorAll('.scp-footnote'));
                            const index = allFn.indexOf(fn);
                            if (index !== -1) {
                                window.location.href = "edit-footnote://" + index;
                            }
                        }
                    });
                }



                // --- Helper Functions for Collapsible Modules ---
                function toggleDiv(header) {
                     var content = header.nextElementSibling;
                     if (content) {
                         if (content.style.display === 'none') {
                             content.style.display = 'block';
                             header.classList.remove('collapsed');
                         } else {
                             content.style.display = 'none';
                             header.classList.add('collapsed');
                         }
                     }
                }
                
                function toggleCss(header) {
                     // Find the css content div
                     var parent = header.parentElement;
                     var content = parent.querySelector('.css-content');
                     if(content) {
                        if (content.style.display === 'none') {
                             content.style.display = 'block';
                             header.innerText = header.innerText.replace(' (点击展开)', ' (点击折叠)');
                         } else {
                             content.style.display = 'none';
                             header.innerText = header.innerText.replace(' (点击折叠)', ' (点击展开)');
                             if(!header.innerText.includes(' (点击展开)')) header.innerText += ' (点击展开)';
                         }
                     }
                }

                // --- Smart Backspace Handler ---
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Backspace') {
                        var sel = window.getSelection();
                        if (sel.rangeCount > 0 && sel.isCollapsed) {
                            var range = sel.getRangeAt(0);
                            var node = range.startContainer;
                            
                            // Traverse up to find the block element if we are in a text node
                            var block = node;
                            while (block && block.nodeType === 3) block = block.parentNode;
                            
                            // Check for empty P or DIV with BR
                            // If it's <p><br></p> or <div><br></div> and empty text
                            if (block && (block.tagName === 'P' || block.tagName === 'DIV')) {
                                if (block.innerText.trim() === '' || block.innerHTML === '<br>') {
                                     // Check Previous and Next Siblings
                                     var prev = block.previousElementSibling;
                                     var next = block.nextElementSibling;
                                     
                                     // Identify components
                                     var isComp = function(el) {
                                         return el && (el.classList.contains('scp-component') || el.classList.contains('div-box') || el.classList.contains('css-box') || el.hasAttribute('data-type'));
                                     };
                                     
                                     if (isComp(prev) && isComp(next)) {
                                         e.preventDefault();
                                         block.remove();
                                         // Optional: Move cursor to end of prev?
                                         // If we remove the line, cursor might be lost. 
                                         // Let's try to set cursor to end of prev.
                                         // But prev is contenteditable=false usually.
                                         // So let's just remove it. Browser usually handles focus.
                                     }
                                }
                            }
                        }
                    }
                });

                window.onload = function() {
                    setupObserver();
                    setupTooltips();
                    refreshFootnotes();
                };
            </script>
        </head>
        <body>
            <div class="rate-module-box" contenteditable="false">
                <div class="rate-controls">
                    <button class="rate-btn rate-align-btn" onclick="rateAction('left', this)">Left</button>
                    <button class="rate-btn" onclick="rateAction('hide', this)">隐藏</button>
                    <button class="rate-btn rate-align-btn" onclick="rateAction('right', this)">Right</button>
                </div>
                <div class="rate-content">[[module Rate]]</div>
            </div>
            <div id="editor-root" contenteditable="true"></div>
            <div id="footnote-list-footer" contenteditable="false"></div>
        </body>
        </html>
        """
        self.browser.setHtml(content)

    def toggle_config_panels(self):
        current = self.comp_selector.currentText()
        self.basalt_group.setVisible(current == "版式")
        self.aim_group.setVisible(current == "AIM 高级信息方法论")

    def toggle_right_dock(self):
        if self.right_dock.isVisible():
            self.right_dock.hide()
        else:
            self.right_dock.show()

    def on_basalt_toggled(self, checked):
        if checked:
            self.check_enable_shivering.setChecked(False)
            self.check_enable_bhl.setChecked(False)
            self.basalt_sub_options_frame.setEnabled(True)
        else:
            self.basalt_sub_options_frame.setEnabled(False)
        self.update_theme_state()

    def on_shivering_toggled(self, checked):
        if checked:
            self.check_enable_basalt.setChecked(False)
            self.check_enable_bhl.setChecked(False)
            self.shivering_sub_options_frame.setEnabled(True)
        else:
            self.shivering_sub_options_frame.setEnabled(False)
        self.update_theme_state()

    def on_bhl_toggled(self, checked):
        if checked:
            self.check_enable_basalt.setChecked(False)
            self.check_enable_shivering.setChecked(False)
            # If BHL is enabled, ensure only one sub-option is checked, default to office if none
            if not self.check_bhl_office.isChecked() and not self.check_bhl_raisa.isChecked():
                self.check_bhl_office.setChecked(True)
            self.bhl_sub_options_frame.setEnabled(True)
        else:
            self.bhl_sub_options_frame.setEnabled(False)
        self.config_changed = True
        self.update_theme_state()

    def on_bhl_office_toggled(self, checked):
        if checked:
            if self.check_bhl_raisa.isChecked():
                self.check_bhl_raisa.setChecked(False)
        self.update_theme_state()

    def on_bhl_raisa_toggled(self, checked):
        if checked:
            if self.check_bhl_office.isChecked():
                self.check_bhl_office.setChecked(False)
        self.update_theme_state()

    def apply_relative_size(self):
        size_str = self.rel_size_selector.currentText()
        if size_str == "自定义":
            val, ok = QInputDialog.getText(self, "自定义相对字号", "请输入值 (如 2em, 200%, smaller):")
            if ok and val:
                size_str = val
            else:
                return
        self.browser.page().runJavaScript(f"applyFontSize('{size_str}');")
        self.browser.setFocus()

    def set_heading(self, index):
        """处理标题选择逻辑"""
        tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6"]
        if 0 <= index < len(tags):
            tag = tags[index]
            self.exec_format("formatBlock", tag)

    def open_link_dialog(self):
        """打开插入链接的对话框"""
        dialog = LinkDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            url, text, new_window = dialog.get_data()
            if url:
                # 如果没有输入文本，默认使用 URL
                display_text = text if text else url
                # 根据 Wikidot 语法，如果是新窗口则前面加 *
                # 但这里是插入 HTML，方便预览，所以用标准 HTML
                target_attr = ' target="_blank"' if new_window else ''
                # 插入 HTML 链接
                html = f'<a href="{url}"{target_attr}>{display_text}</a>'
                self.browser.page().runJavaScript(f"""
                    document.execCommand('insertHTML', false, '{html}');
                """)

    def exec_format(self, command, value=None):
        self.browser.page().runJavaScript(f"document.execCommand('{command}', false, {json.dumps(value)});")
        self.browser.setFocus()

    def apply_font_size(self, size_str=None):
        if not size_str: size_str = self.size_selector.currentText()
        if size_str == "自定义px":
            px, ok = QInputDialog.getText(self, "自定义字号", "请输入像素值:")
            if ok:
                size_str = px if 'px' in px else px + 'px'
            else:
                return
        self.browser.page().runJavaScript(f"applyFontSize('{size_str}');")
        self.browser.setFocus()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid(): self.exec_format("foreColor", color.name())

    def insert_hr(self):
        self.run_insert_js('<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div><p><br></p>')

    def insert_toc(self):
        # 插入目录组件
        self.run_insert_js(
            '<div class="scp-component" data-type="toc" contenteditable="false" style="border: 1px dashed #999; padding: 5px; background: #f0f0f0;"><b>目录 (TOC)</b><br>[[toc]]</div><p><br></p>')

    def insert_table(self):
        # 插入3x3表格
        self.browser.page().runJavaScript("insertTable();")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.source_display.toPlainText())
        QMessageBox.information(self, "成功", "代码已复制到剪切板！")

    def insert_component(self):
        comp = self.comp_selector.currentText()
        html = ""

        # 如果选择的是版式
        if comp == "版式":
            # 仅更新状态，不插入HTML
            self.update_theme_state()
            QMessageBox.information(self, "版式更新", "版式设置已更新！请查看右侧面板确认状态。")
            return

        elif comp == "AIM 高级信息方法论":
            blocks_attr = ""
            row_style_top = ""
            row_style_bottom = ""
            footer_text = "AIM 完整版头"

            if self.radio_aim_top.isChecked():
                blocks_attr = 'data-blocks="-"'
                row_style_bottom = 'style="display:none;"'
                footer_text = "仅上半部分的 AIM 示例"
            elif self.radio_aim_bottom.isChecked():
                blocks_attr = 'data-blocks="!"'
                row_style_top = 'style="display:none;"'
                footer_text = "仅下半部分的 AIM 示例"

            # 修复：移除f-string中的多行缩进，改为紧凑格式，防止插入时产生额外的文本节点（空格）
            # 新增：追加空行 <p><br></p> 解决无法编辑下方内容问题
            html = f'''<div class="scp-component aim-box" data-type="aim" {blocks_attr} contenteditable="false"><table class="aim-table"><tr {row_style_top}><td colspan="2"><div class="aim-label">项目编号</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">SCP-XXXX</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">等级 / 公开</div><div class="aim-value" data-field="lv" contenteditable="true">等级-01/公开</div></td></tr><tr {row_style_top}><td colspan="2"><div class="aim-label">收容等级</div><div class="aim-value" data-field="cc" contenteditable="true">THAUMIEL</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">扰动等级</div><div class="aim-value" data-field="dc" contenteditable="true">DARK</div></td></tr><tr {row_style_bottom} style="text-align: center; background: #fafafa;"><td><div class="aim-label">负责站点</div><div class="aim-value" data-field="site" contenteditable="true">Site-0</div></td><td><div class="aim-label">站点主管</div><div class="aim-value" data-field="dir" contenteditable="true">Dr 主管</div></td><td><div class="aim-label">首席研究员</div><div class="aim-value" data-field="head" contenteditable="true">Dr 博士</div></td><td><div class="aim-label">指派特遣队</div><div class="aim-value" data-field="mtf" contenteditable="true">Alpha-1</div></td></tr></table><div class="aim-footer">{footer_text}</div></div><p><br></p>'''

        elif comp == "图片块 (Image Block)":
            # 增加 .img-toggle-btn 用于隐藏/显示控制栏，包裹 input 和 buttons 在 .img-controls-wrapper 中
            # 移除开头的 &nbsp; 锚点，防止生成多余空格
            # 移除 clear:both 以允许文字环绕
            html = '''<span>&nbsp;</span><div class="scp-component image-block-box" data-type="image-block" data-align="right" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div><div style="background:#fff; padding:5px; text-align:center; border-bottom:1px solid #eee; font-size:0.9em;"><b>源:</b> <span data-field="name" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:50px; display:inline-block; border-bottom:1px dashed #ccc;">link/to/image.jpg</span></div></div><div class="image-block-content"><img src="" class="img-preview" style="max-width:100%; display:none; margin:0 auto 5px auto;"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">在此输入图片描述</span></div></div><span>&nbsp;</span>'''

        elif comp == "高级图片块 (Advanced Image)":
            # 移除开头的 &nbsp; 锚点，防止生成多余空格
            # 移除 clear:both 以允许文字环绕
            html = '''<div class="scp-component image-block-box" data-type="image-block-adv" data-align="right" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div><div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div><b>源:</b> <span data-field="name" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:50px; display:inline-block; border-bottom:1px dashed #ccc;">link/to/image.jpg</span></div><div><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span> <b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span></div></div></div><div class="image-block-content"><img src="" class="img-preview" style="max-width:100%; display:none; margin:0 auto 5px auto;"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">在此输入图片描述</span></div></div><span>&nbsp;</span>'''

        elif "Tab View" in comp:
            html = '''<div class="scp-component tabview-box" data-type="tabview" contenteditable="false"><div class="tab-header"><span class="tab-btn active" onclick="selectTab(this)" contenteditable="true">Tab 1</span><span class="tab-btn" onclick="selectTab(this)" contenteditable="true">Tab 2</span><span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents"><div class="tab-item active" contenteditable="true"><p>Tab 1 Content...</p></div><div class="tab-item" contenteditable="true"><p>Tab 2 Content...</p></div></div></div><p><br></p>'''

        elif "User" in comp:
            html = '''<span class="scp-component user-tag" data-type="user" contenteditable="false"><div class="user-icon"></div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">User Name</span></span>'''

        elif comp == "高级用户信息 (Advanced User)":
            html = '''<span class="scp-component user-tag" data-type="user-adv" contenteditable="false"><div class="user-icon" style="background:gold; text-align:center; line-height:12px; font-size:10px; color:#fff;">★</div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">User Name</span></span>'''

        elif "ACS" in comp:
            html = '''<div class="scp-component acs-box" data-type="acs" data-clearance="2" data-container="euclid" data-secondary="none" data-disruption="vlam" data-risk="notice" style="--acs-color: #f1c40f;" contenteditable="false"><div class="acs-header-row" contenteditable="false"><div class="acs-title">SCP-CN 异常分级栏</div><div class="acs-anim-toggle"><span>动画:</span><label class="switch"><input type="checkbox" class="acs-anim-checkbox"><span class="slider"></span></label></div><div class="acs-item-num" contenteditable="true" data-field="item-number">SCP-CN-XXXX</div></div><div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 10px;"><div><small style="color:#888; font-size:9px; text-transform:uppercase;">许可等级</small><br><b data-field="clearance" contenteditable="true">2级</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">项目等级</small><br><b data-field="container" style="color:var(--acs-color)" contenteditable="true">Euclid</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">次要等级</small><br><b data-field="secondary" contenteditable="true">none</b><div style="font-size:0.8em; border-top:1px solid #ccc; margin-top:2px;">Icon: <span data-field="secondary-icon" contenteditable="true" style="min-width:20px; display:inline-block"></span></div></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">扰动等级</small><br><b data-field="disruption" contenteditable="true">Vlam</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">风险等级</small><br><b data-field="risk" contenteditable="true">Notice</b></div></div></div><p><br></p>'''

        elif "折叠块" in comp:
            html = '''<div class="scp-component collapsible-box open" data-type="collapsible" contenteditable="false"><div class="collapsible-header"><span><span class="title-label">显示标题:</span> <span class="title-input" data-field="show" contenteditable="true">+ 打开折叠内容</span></span><span><span class="title-label">隐藏标题:</span> <span class="title-input" data-field="hide" contenteditable="true">- 关闭折叠内容</span></span></div><div class="collapsible-content-area" contenteditable="true"><p>在这里输入折叠内的内容...</p></div></div><p><br></p>'''

        elif "DIV 模块" in comp:
            html = '''<div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="example"</div><div class="div-content" contenteditable="true"><p>输入正文...</p></div></div><p><br></p>'''

        elif "CSS 模块" in comp:
            html = '''<div class="scp-component css-box" data-type="css-module" contenteditable="false"><div class="css-header">CSS Module (Valid CSS Only)</div><div class="css-content" contenteditable="true">/* Input CSS here */</div><div class="css-hint">被css影响的代码紧跟css模块下面</div></div><p><br></p>'''

        elif "授权引用" in comp:
            self.browser.page().runJavaScript("insertLicenseBox()")
            return

        elif "脚注" in comp:
            self.insert_new_footnote()
            return

        if html:
            # Fix: Insert with collapse to avoid deleting previous content
            safe_html = html.replace('\n', ' ').replace("'", "\\'")
            js = f"""
            (function() {{
                var sel = window.getSelection();
                if (sel.rangeCount) {{
                    var range = sel.getRangeAt(0);
                    range.collapse(false); // Force collapse to end
                    var fragment = range.createContextualFragment('{safe_html}');
                    range.insertNode(fragment);
                    if (fragment.lastChild) range.setStartAfter(fragment.lastChild);
                    range.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(range);
                    if (typeof refreshFootnotes === 'function') refreshFootnotes();
                }}
            }})();
            """
            self.browser.page().runJavaScript(js)

        # 每次插入组件也顺带更新一次全局状态（特别是Better Footnotes可能变更）
        self.update_theme_state()

    def update_theme_state(self):
        """根据UI控件状态更新内部配置，并同步到右侧面板"""
        if not hasattr(self, 'lbl_bf_status') or not hasattr(self, 'lbl_theme_status'):
             return

        # 1. 更新 Better Footnotes 状态
        self.use_better_footnotes = self.check_better_footnotes.isChecked()
        bf_text = "开启" if self.use_better_footnotes else "关闭"
        self.lbl_bf_status.setText(f"<b>Better Footnotes:</b> {bf_text}")

        # 2. 更新版式状态
        if self.check_enable_basalt.isChecked():
            self.page_theme_config["type"] = "basalt"
            opts = []
            if self.check_dark.isChecked(): opts.append("darkmode=a")
            if self.check_wide.isChecked(): opts.append("wide=a")
            if self.check_hidetitle.isChecked(): opts.append("hidetitle=a")
            self.page_theme_config["options"] = opts

            theme_text = "玄武岩 (Basalt)"
            if opts:
                theme_text += f"<br>选项: {', '.join(opts)}"
            self.lbl_theme_status.setText(f"<b>当前版式:</b> {theme_text}")

        elif self.check_enable_shivering.isChecked():
            self.page_theme_config["type"] = "shivering"
            self.page_theme_config["options"] = [] 
            
            sub_text = "默认"
            code_suffix = ""
            if self.radio_shiv_mo.isChecked():
                sub_text = "澳门"
                code_suffix = " mo=*"
            elif self.radio_shiv_kl.isChecked():
                sub_text = "吉隆坡"
                code_suffix = " kl=*"
            elif self.radio_shiv_dub.isChecked():
                sub_text = "都柏林"
                code_suffix = " dub=*"
            elif self.radio_shiv_ct.isChecked():
                sub_text = "开普敦"
                code_suffix = " ct=*"
            elif self.radio_shiv_ba.isChecked():
                sub_text = "布宜诺斯艾利斯"
                code_suffix = " ba=*"
            
            self.page_theme_config["shivering_suffix"] = code_suffix
            self.lbl_theme_status.setText(f"<b>当前版式:</b> 夜琉璃 ({sub_text})")

        elif self.check_enable_bhl.isChecked():
            self.page_theme_config["type"] = "bhl"
            
            sub_opts = []
            if self.check_dark_sidebar.isChecked(): sub_opts.append("暗色侧边栏")
            if self.check_bhl_collapsible.isChecked(): sub_opts.append("可折叠侧边栏")
            if self.check_bhl_toggle.isChecked(): sub_opts.append("切换侧边栏")
            if self.check_bhl_centered.isChecked(): sub_opts.append("居中页眉")
            if self.check_bhl_office.isChecked(): sub_opts.append("办公室")
            if self.check_bhl_raisa.isChecked(): sub_opts.append("RAISA Sigma-9")
            
            theme_text = "黑色标记笔 (Black Highlighter)"
            if sub_opts:
                theme_text += f"<br>选项: {', '.join(sub_opts)}"
            
            self.lbl_theme_status.setText(f"<b>当前版式:</b> {theme_text}")
            
            # Store BHL options
            self.page_theme_config["bhl_options"] = {
                "dark_sidebar": self.check_dark_sidebar.isChecked(),
                "collapsible": self.check_bhl_collapsible.isChecked(),
                "toggle": self.check_bhl_toggle.isChecked(),
                "centered": self.check_bhl_centered.isChecked(),
                "office": self.check_bhl_office.isChecked(),
                "raisa": self.check_bhl_raisa.isChecked()
            }

        else:
            self.page_theme_config["type"] = "none"
            self.page_theme_config["options"] = []
            self.lbl_theme_status.setText("<b>当前版式:</b> 无")

        # 3. 更新暗色侧边栏状态 (UI Feedback)
        # Only relevant if BHL is active and Dark Sidebar is checked
        is_ds = self.check_enable_bhl.isChecked() and self.check_dark_sidebar.isChecked()
        sidebar_text = "开启" if is_ds else "关闭"
        if hasattr(self, 'lbl_sidebar_status'):
             self.lbl_sidebar_status.setText(f"<b>Dark Sidebar:</b> {sidebar_text}")
        """根据UI控件状态更新内部配置，并同步到右侧面板"""
        if not hasattr(self, 'lbl_bf_status') or not hasattr(self, 'lbl_theme_status'):
             return

        # 1. 更新 Better Footnotes 状态
        self.use_better_footnotes = self.check_better_footnotes.isChecked()
        bf_text = "开启" if self.use_better_footnotes else "关闭"
        self.lbl_bf_status.setText(f"<b>Better Footnotes:</b> {bf_text}")

        # 2. 更新版式状态
        if self.check_enable_basalt.isChecked():
            self.page_theme_config["type"] = "basalt"
            opts = []
            if self.check_dark.isChecked(): opts.append("darkmode=a")
            if self.check_wide.isChecked(): opts.append("wide=a")
            if self.check_hidetitle.isChecked(): opts.append("hidetitle=a")
            self.page_theme_config["options"] = opts

            theme_text = "玄武岩 (Basalt)"
            if opts:
                theme_text += f"<br>选项: {', '.join(opts)}"
            self.lbl_theme_status.setText(f"<b>当前版式:</b> {theme_text}")

        elif self.check_enable_shivering.isChecked():
            self.page_theme_config["type"] = "shivering"
            self.page_theme_config["options"] = [] # Not used slightly
            
            sub_text = "默认"
            code_suffix = ""
            if self.radio_shiv_mo.isChecked():
                sub_text = "澳门"
                code_suffix = " mo=*"
            elif self.radio_shiv_kl.isChecked():
                sub_text = "吉隆坡"
                code_suffix = " kl=*"
            elif self.radio_shiv_dub.isChecked():
                sub_text = "都柏林"
                code_suffix = " dub=*"
            elif self.radio_shiv_ct.isChecked():
                sub_text = "开普敦"
                code_suffix = " ct=*"
            elif self.radio_shiv_ba.isChecked():
                sub_text = "布宜诺斯艾利斯"
                code_suffix = " ba=*"
            
            self.page_theme_config["shivering_suffix"] = code_suffix
            self.lbl_theme_status.setText(f"<b>当前版式:</b> 夜琉璃 ({sub_text})")

        # 3. 更新暗色侧边栏状态
        is_dark_sidebar = self.check_dark_sidebar.isChecked()
        self.page_theme_config["dark_sidebar"] = is_dark_sidebar
        sidebar_text = "开启" if is_dark_sidebar else "关闭"
        if hasattr(self, 'lbl_sidebar_status'):
             self.lbl_sidebar_status.setText(f"<b>Dark Sidebar:</b> {sidebar_text}")

        else:
            self.page_theme_config["type"] = "none"
            self.page_theme_config["options"] = []
            self.lbl_theme_status.setText("<b>当前版式:</b> 无")

    def insert_new_footnote(self):
        js = """
        (function(){
            var fns = document.querySelectorAll('.scp-footnote');
            var nextNum = fns.length + 1;
            var span = document.createElement('span');
            span.className = 'scp-component scp-footnote';
            span.setAttribute('data-type', 'footnote');
            span.setAttribute('data-content', '新脚注内容');
            span.setAttribute('contenteditable', 'false');
            span.innerText = nextNum;
            var sel = window.getSelection();
            if (sel.rangeCount) {
                var range = sel.getRangeAt(0);
                range.insertNode(span);
                range.setStartAfter(span);
                range.collapse(true);
                sel.removeAllRanges(); sel.addRange(range);
            }
            refreshFootnotes();
        })()
        """
        self.browser.page().runJavaScript(js)

    def open_footnote_editor(self, index):
        """Called via CustomWebPage when a footnote is clicked"""
        # We need to get current content first. 
        # Since we have the index, we can target it directly via JS.
        js = f"document.querySelectorAll('.scp-footnote')[{index}].getAttribute('data-content')"
        
        def on_got(content):
            if content is None: content = ""
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑脚注", "内容:", content)
            if ok:
                # Update content and title
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
        
        # Detect Footnote Index
        js_fn_idx = f"(function(){{ var el = document.elementFromPoint({pos.x()}, {pos.y()}); return el ? Array.from(document.querySelectorAll('.scp-footnote')).indexOf(el.closest('.scp-footnote')) : -1; }})()"

        full_js = f"JSON.stringify({{ comp: {js}, table: {js_table}, tabBtn: {js_tab_btn}, fnIdx: {js_fn_idx} }})"
        self.browser.page().runJavaScript(full_js, lambda res: self.show_menu(pos, json.loads(res)))

    def show_menu(self, pos, res):
        menu = QMenu()
        c_type = res.get('comp')
        in_table = res.get('table')
        is_tab_btn = res.get('tabBtn')
        fn_idx = res.get('fnIdx', -1)

        # 增加通用粘贴选项 (因为接管了右键菜单，默认粘贴可能失效)
        paste_act = menu.addAction("粘贴")
        paste_act.triggered.connect(lambda: self.browser.page().triggerAction(QWebEnginePage.WebAction.Paste))
        menu.addSeparator()

        if fn_idx != -1:
            menu.addAction("编辑脚注").triggered.connect(lambda: self.open_footnote_editor(fn_idx))
            menu.addSeparator()

        if c_type:
            # Special case for tabview buttons, handled separately below?
            # Actually, deleting component removes whole tabview.
            # We want specific actions for tabs if clicked on tab button.

            if c_type == 'tabview' and is_tab_btn:
                menu.addAction("删除该选项卡").triggered.connect(lambda: self.browser.page().runJavaScript(
                    f"removeTab(document.elementFromPoint({pos.x()}, {pos.y()}))"))
                menu.addSeparator()

            del_act = menu.addAction(f"删除该组件")
            del_act.triggered.connect(lambda: self.remove_component_at_pos(pos))

            if c_type == 'acs':
                # Primary Class Menu
                cm = menu.addMenu("修改等级颜色 (主等级)")
                primary_classes = ["Safe", "Euclid", "Keter", "Neutralized", "Pending", "Explained", "Esoteric"]
                for cls in primary_classes:
                    act = cm.addAction(cls)
                    act.triggered.connect(lambda checked, c=cls: self.change_acs_class(pos, c))

                # Secondary Class Menu
                sm = menu.addMenu("设置次要等级")
                secondary_classes = ["Apollyon", "Archon", "Cernunnos", "Hiemal", "Tiamat", "Ticonderoga", "Thaumiel",
                                     "None"]
                for cls in secondary_classes:
                    act = sm.addAction(cls)
                    act.triggered.connect(lambda checked, c=cls: self.change_acs_secondary(pos, c))
            
            # Add "New Line Below" for non-image components
            if c_type not in ['image-block', 'image-block-adv']:
                 menu.addSeparator()
                 menu.addSeparator()
                 menu.addAction("在下面换行").triggered.connect(lambda: self.insert_newline_after_component(pos))

        if c_type in ['css-module', 'div-block']:
            menu.addSeparator()
            menu.addAction("快捷代码：终端样式").triggered.connect(lambda: self.apply_terminal_shortcut(pos))
            menu.addAction("快捷代码：终端 #001").triggered.connect(lambda: self.apply_terminal_001(pos))
            menu.addAction("快捷代码：RAISA通知").triggered.connect(lambda: self.apply_raisa_notice(pos))
            menu.addAction("快捷代码：XXXX级机密").triggered.connect(lambda: self.apply_class_warning(pos))
            menu.addAction("快捷代码：O5议会命令").triggered.connect(lambda: self.apply_o5_command(pos))
            menu.addAction("快捷代码：视频/音频记录1").triggered.connect(lambda: self.apply_video_record(pos))
            menu.addAction("快捷代码：视频/音频记录2").triggered.connect(lambda: self.apply_video_record2(pos))
            menu.addAction("快捷代码：便签纸").triggered.connect(lambda: self.apply_page_note(pos))
            menu.addAction("快捷代码：登入/登出").triggered.connect(lambda: self.apply_login_logout(pos))


        if in_table:
            t_menu = menu.addMenu("表格操作")
            t_menu.addAction("增加行").triggered.connect(
                lambda: self.browser.page().runJavaScript("tableAction('addRow')"))
            t_menu.addAction("删除行").triggered.connect(
                lambda: self.browser.page().runJavaScript("tableAction('delRow')"))
            t_menu.addAction("增加列").triggered.connect(
                lambda: self.browser.page().runJavaScript("tableAction('addCol')"))
            t_menu.addAction("删除列").triggered.connect(
                lambda: self.browser.page().runJavaScript("tableAction('delCol')"))
            t_menu.addAction("向右合并 (删除竖线)").triggered.connect(
                lambda: self.browser.page().runJavaScript("tableAction('mergeRight')"))
            t_menu.addAction("隐藏/显示边框").triggered.connect(
                lambda: self.browser.page().runJavaScript("tableAction('toggleBorder')"))
            t_menu.addSeparator()
            t_menu.addAction("删除表格").triggered.connect(
                lambda: self.browser.page().runJavaScript("tableAction('delTable')"))

        if not c_type and not in_table:
            add_fn = menu.addAction("插入脚注")
            add_fn.triggered.connect(self.insert_new_footnote)

        menu.exec(self.browser.mapToGlobal(pos))

    def insert_newline_after_component(self, pos):
        """Helper to insert a newline after the component at the given position"""
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
        """
        Apply Terminal Style:
        1. Insert [[module CSS]] at top with specific style.
        2. Insert [[div class="danke agent"]] below component.
        3. Disable other themes.
        """
        term_css = """
.danke{
padding: 5px 5px 5px 15px;
margin-bottom:10px;
font-family: monospace;
font-size: 1.1em; }

.agent{
background-color:#000000;
border: 3px solid #55AA55;
color: #77CC77;
}

.site{
background-color:#222200;
border: 3px solid #AAAA55;
color: #DDDD77;
}
"""
        term_div_content = """<div class="div-header" contenteditable="true">DIV: class="danke agent"</div><div class="div-content" contenteditable="true">| 细节<br>| 细节<br>| 细节<br>| 细节<br>| 细节<br><br>文字 文字 文字<br>更多文字<br><br>更多<br><br>以及更多<br><br>甚至还有更多要记录的文字</div>"""
        
        # Escape for JS
        safe_css = term_css.replace('\n', '\\n').replace('"', '\\"')
        safe_div = term_div_content.replace('\n', '\\n').replace('"', '\\"')

        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component') : null;
            var type = comp ? comp.getAttribute('data-type') : null;

            var cssContent = "{safe_css}";
            var divHtml = '{safe_div}';
            
            // Helper to create CSS Element
            function createCssEl() {{
                var box = document.createElement('div');
                box.className = 'scp-component css-box';
                box.setAttribute('data-type', 'css-module');
                box.setAttribute('contenteditable', 'false');
                box.innerHTML = '<details open><summary class="css-header" style="cursor:pointer; user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
                return box;
            }}
            
            // Helper to create Div Element
            function createDivEl() {{
                var divBox = document.createElement('div');
                divBox.className = 'scp-component div-box';
                divBox.setAttribute('data-type', 'div-block');
                divBox.setAttribute('contenteditable', 'false');
                divBox.innerHTML = '{safe_div}';
                return divBox;
            }}
            
            // Helper: Check if Generic Terminal css exists
            function hasTerminalCss() {{
                 var css = document.querySelectorAll('.css-box .css-content');
                 for(var i=0; i<css.length; i++) {{
                     if(css[i].innerText.indexOf('.danke') !== -1 && css[i].innerText.indexOf('.agent') !== -1) return true;
                 }}
                 return false;
            }}

            if (type === 'css-module') {{
                // CASE 1: Right-clicked a CSS Module -> Replace it & Ensure Div below
                
                // Replace Content with Collapsible Structure
                comp.innerHTML = '<details open><summary class="css-header" style="cursor:pointer; user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
                
                // Check Next Sibling
                var next = comp.nextElementSibling;
                var needDiv = true;
                if (next && next.classList.contains('div-box')) {{
                    // Check if it looks like a generic terminal div (has danke agent in header)
                    var header = next.querySelector('.div-header');
                    if (header && (header.innerText.indexOf('danke') !== -1 || header.innerText.indexOf('agent') !== -1)) {{
                        needDiv = false; // Already paired
                    }}
                }}
                
                if (needDiv) {{
                     comp.parentNode.insertBefore(createDivEl(), comp.nextSibling);
                }}

            }} else if (type === 'div-block') {{
                // CASE 2: Right-clicked a Div Module -> Replace it & Ensure CSS at top
                
                // Replace this div with Generic Terminal Div
                var newDiv = createDivEl();
                comp.parentNode.replaceChild(newDiv, comp);
                
                // Ensure CSS exists at top
                if (!hasTerminalCss()) {{
                    editor.insertBefore(createCssEl(), editor.firstChild);
                }}

            }} else {{
                // CASE 3: Fallback (Clicking empty space or other component)
                // Insert CSS at top if missing, insert Div at cursor
                
                if (!hasTerminalCss()) {{
                    editor.insertBefore(createCssEl(), editor.firstChild);
                }}
                
                if (comp) {{
                     comp.parentNode.insertBefore(createDivEl(), comp.nextSibling);
                }} else {{
                     editor.appendChild(createDivEl());
                }}
            }}
            
            // Trigger Style Update (Generic uses same updater currently)
            if(typeof updateTerminalStyle === 'function') updateTerminalStyle();
        }})()
        """
        self.browser.page().runJavaScript(js)
        
        # Disable Themes in UI
        self.check_enable_basalt.setChecked(False)
        self.check_enable_shivering.setChecked(False)
        self.check_enable_bhl.setChecked(False)
        # Force update
        self.update_theme_state()

    def apply_terminal_001(self, pos):
        # 1. CSS Content
        term_css = """
div.terminal{
    border: 1px solid black;
    border: solid 3px #BBBBBB;
    border-radius: 16px;
    background-color: #000000;
/* 终端上方的黑色阴影 */
    background-image:
        radial-gradient(ellipse 1000% 100% at 50% 90%, transparent, #121);
    background-position: center;
    display: block;
/* 终端周围的阴影 */
    box-shadow: inset 0 0 10em 1em rgba(0,0,0,0.5);
/* 防止扫描条产生滚动条 */
    overflow:hidden;
}
div.terminal blockquote {
    background-color: black;
    border: double 3px #80FF80;
    color: #80FF80;
}
div.scanline{
    margin-top: -40%;
    width: 100%;
    height: 60px;
    position: relative;
    pointer-events: none;
/* Safari 4.0 - 8.0 */
    -webkit-animation: scan 12s linear 0s infinite; /* 你可能需要修改这个。如果扫描条走得太快了，添加5秒。 */
    animation: scan 12s linear 0s infinite; /* 同上 */
    background: linear-gradient(to bottom, rgba(56, 112, 82,0), rgba(56, 112, 82,0.1)) !important;
}

div.text{
    color: rgba(128,255,128,0.8);
    padding-left: 2em;
    padding-top: 40%;
    font-family: monospace;
    font-size: 1.2em;
    }

/* Safari 4.0 - 8.0 */
@-webkit-keyframes scan{
    from{ transform: translateY(-10%);}
    to{  transform: translateY(5000%);} /* 你可能需要根据你终端的长短修改这个。如果扫描条走到一半停止了，增大第二个数字。 */
}

@keyframes scan{
    from{ transform: translateY(-10%);}
    to{  transform: translateY(5000%);} /* 同上。 */
}

div.text a {
    color: #90EE90;
    text-decoration: none;
    background: transparent;
}
div.text a.newpage {
    color: #90EE90;
    text-decoration: none;
    background: transparent;
}
div.text a:hover {
    color: #131;
    text-decoration: underline;
    background-color: #80FF80;
    padding: 1px;
}
div.text a:hover::before{
content: "> ";
}
"""
        # 2. HTML Content (Nested Divs)
        # Note: We construct nested div-box components manually to ensure correct structure.
        # Minified to prevent whitespace/newline issues in export and remove comments
        # @@@@ replaced with <p><br></p> for visual rendering while preserving export capability via parse_node
        # @@------@@ replaced with <span class="terminal-hr">------</span> for visual dashes
        # ADDED 'terminal' class to outer div for robust styling persistence
        term_html = """<div class="scp-component div-box terminal" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="terminal"</div><div class="div-content" contenteditable="true"><div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="scanline"</div><div class="div-content" contenteditable="true"></div></div><div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="text"</div><div class="div-content" contenteditable="true"><div style="text-align: center;"><span style="font-size: 150%;"><u>终端 #001</u></span><br><p><br></p><p><br></p><span class="terminal-hr">------</span><br>欢迎，用户<br><span class="terminal-hr">------</span><br></div><p><br></p><p><br></p><p><br></p><blockquote>终端内部的链接会在鼠标移过时显示“&gt;”。<br><a href="http://www.baidu.com">就像这样</a></blockquote><br>谢谢你查看我的格式！<br><p><br></p><p><br></p></div></div></div></div>"""

        # Escape strings for JS
        safe_css = term_css.replace('\n', '\\n').replace('"', '\\"')
        safe_html_js = term_html.replace('\n', '\\n').replace('"', '\\"')

        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component') : null;
            var type = comp ? comp.getAttribute('data-type') : null;

            var cssContent = "{safe_css}";
            var divHtml = '{safe_html_js}';
            
            // Helper to create CSS Element
            function createCssEl() {{
                var box = document.createElement('div');
                box.className = 'scp-component css-box';
                box.setAttribute('data-type', 'css-module');
                box.setAttribute('contenteditable', 'false');
                box.innerHTML = '<details open><summary class="css-header" style="cursor:pointer; user-select:none;">CSS Module (Terminal #001) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
                return box;
            }}
            
            // Helper to create Div Element
            function createDivEl() {{
                return document.createRange().createContextualFragment(divHtml);
            }}
            
            // Helper: Check if global terminal css exists (roughly)
            function hasTerminalCss() {{
                 var css = document.querySelectorAll('.css-box .css-content');
                 for(var i=0; i<css.length; i++) {{
                     if(css[i].innerText.indexOf('.danke') !== -1 && css[i].innerText.indexOf('.agent') !== -1) return true;
                 }}
                 return false;
            }}

            if (type === 'css-module') {{
                // CASE 1: Right-clicked a CSS Module -> Replace it & Ensure Div below
                
                // Replace Content with Collapsible Structure (Force "Terminal Style" structure)
                comp.innerHTML = '<details open><summary class="css-header" style="cursor:pointer; user-select:none;">CSS Module (Terminal #001) - 点击折叠/展开</summary><div class="css-content" contenteditable="true">' + cssContent + '</div></details><div class="css-hint">被css影响的代码紧跟css模块下面</div>';
                
                // Check Next Sibling
                var next = comp.nextElementSibling;
                var needDiv = true;
                if (next && next.classList.contains('div-box')) {{
                    // Check if it looks like a terminal div (has 'terminal' class)
                    // We can check header text or content
                    var header = next.querySelector('.div-header');
                    if (header && header.innerText.indexOf('terminal') !== -1) {{
                        needDiv = false; // Already paired
                    }}
                }}
                
                if (needDiv) {{
                     comp.parentNode.insertBefore(createDivEl(), comp.nextSibling);
                }}

            }} else if (type === 'div-block') {{
                // CASE 2: Right-clicked a Div Module -> Replace it & Ensure CSS at top
                
                // Replace this div with Terminal Div
                var newDiv = createDivEl();
                comp.parentNode.replaceChild(newDiv, comp);
                
                // Ensure CSS exists at top
                if (!hasTerminalCss()) {{
                    editor.insertBefore(createCssEl(), editor.firstChild);
                }}

            }} else {{
                // CASE 3: Fallback (Clicking empty space or other component)
                // Insert CSS at top if missing, insert Div at cursor
                
                if (!hasTerminalCss()) {{
                    editor.insertBefore(createCssEl(), editor.firstChild);
                }}
                
                if (comp) {{
                     var newDiv = createDivEl();
                     comp.parentNode.insertBefore(newDiv, comp.nextSibling);
                }} else {{
                     editor.appendChild(createDivEl());
                }}
            }}
            
            // 3. Trigger Style Update
            if(typeof updateTerminalStyle === 'function') updateTerminalStyle();
        }})();
        """
        self.browser.page().runJavaScript(js)

    def apply_raisa_notice(self, pos):
        """Insert RAISA Notice Div"""
        # RAISA Style
        style = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5;"
        
        js = f"""
        (function() {{
            try {{
                var editor = document.getElementById('editor-root');
                var x = {pos.x()};
                var y = {pos.y()};
                var el = document.elementFromPoint(x, y);
                var comp = null;
                
                if (el) {{
                    comp = el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box');
                }}
                
                // Fallback to cursor position if click didn't hit a component
                if (!comp) {{
                     var sel = window.getSelection();
                     if (sel.rangeCount > 0) {{
                         var range = sel.getRangeAt(0);
                         var node = range.startContainer;
                         if (node.nodeType === 3) node = node.parentNode;
                         if (node) comp = node.closest('.scp-component');
                     }}
                }}

                // Create Outer Box
                var divBox = document.createElement('div');
                divBox.className = 'scp-component raisa-box'; 
                divBox.setAttribute('data-type', 'raisa-notice');
                divBox.setAttribute('contenteditable', 'false');
                
                // Apply WYSIWYG Style directly
                divBox.style.cssText = "{style} position: relative; clear: both;";
                
                // Create Content
                var divContent = document.createElement('div');
                divContent.className = 'raisa-content';
                divContent.setAttribute('contenteditable', 'true');
                
                // Inner Centered Container
                var centerDiv = document.createElement('div');
                centerDiv.style.textAlign = 'center';
                centerDiv.className = 'raisa-inner';
                
                // Title
                var titleSpan = document.createElement('span');
                titleSpan.style.fontSize = 'larger';
                var strong = document.createElement('strong');
                strong.innerText = '基金会记录与信息安全管理部的通知';
                titleSpan.appendChild(strong);
                
                centerDiv.appendChild(titleSpan);
                centerDiv.appendChild(document.createElement('br'));
                centerDiv.appendChild(document.createElement('br'));
                
                // Body
                centerDiv.appendChild(document.createTextNode('通知在此'));
                centerDiv.appendChild(document.createElement('br'));
                centerDiv.appendChild(document.createElement('br'));
                
                // Signature
                centerDiv.appendChild(document.createTextNode('— Maria Jones，RAISA主管'));
                
                divContent.appendChild(centerDiv);
                divBox.appendChild(divContent);
                
                // Insert or Replace
                if (comp) {{
                    // Hand Feel Optimization: Replace existing generic DIV or CSS module if clicked
                    if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                        comp.parentNode.replaceChild(divBox, comp);
                    }} else {{
                        comp.parentNode.insertBefore(divBox, comp.nextSibling);
                    }}
                }} else {{
                    if (editor) {{
                        editor.appendChild(divBox);
                    }} else {{
                        console.error('Editor root not found');
                    }}
                }}
                
                // Ensure space after
                var br = document.createElement('br');
                if (divBox.nextSibling) {{
                    divBox.parentNode.insertBefore(br, divBox.nextSibling);
                }} else {{
                    divBox.parentNode.appendChild(br);
                }}
            }} catch(e) {{
                console.error("Error applying RAISA notice:", e);
            }}
        }})();
        """
        self.browser.page().runJavaScript(js)

    def apply_class_warning(self, pos):
        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box') : null;
            
            // Create Outer Box with specific class and type for "class-warning"
            var divBox = document.createElement('div');
            divBox.className = 'scp-component class-warning-box'; 
            divBox.setAttribute('data-type', 'class-warning');
            divBox.setAttribute('contenteditable', 'false');
            
            // Apply Style directly
            // Note: float: center is invalid CSS, replaced with margin: 0 auto or equivalent text-align center on parent?
            // User code: float: center; -> Wikidot parses this? Browsers handle float:center as none usually.
            // But we can replicate the visual using margin: auto if display block.
            // Actually, the user asked for "float: center" in the code. I should stick to the requested code for export, but visual might need tweaks.
            // For visual, I'll use margin: 0 auto; to center it block-level.
            var style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) center no-repeat; border: solid 2px #000; padding: 1px 15px; box-shadow: 0 1px 3px rgba(0,0,0,.2); margin: 10px auto; width: fit-content;";
            
            divBox.style.cssText = style + " position: relative; clear: both;";
            
            // Create Content
            var divContent = document.createElement('div');
            divContent.className = 'class-warning-content';
            divContent.setAttribute('contenteditable', 'true');
            
            // Inner Centered Container
            var centerDiv = document.createElement('div');
            centerDiv.style.textAlign = 'center';
            centerDiv.className = 'class-warning-inner';
            
            // Line 1: ##ff5c48|[[size 150%]] **...** [[/size]]##
            var span1 = document.createElement('span');
            span1.style.color = '#ff5c48';
            var span2 = document.createElement('span');
            span2.style.fontSize = '150%';
            var strong1 = document.createElement('strong');
            strong1.textContent = '警告：下列文件为#/XXXX级机密';
            span2.appendChild(strong1);
            span1.appendChild(span2);
            centerDiv.appendChild(span1);
            
            // Line 2: ----
            var hr = document.createElement('hr');
            hr.style.border = 'none';
            hr.style.borderTop = '1px solid #777'; // Visual approx
            hr.style.margin = '10px 0';
            centerDiv.appendChild(hr);
            
            // Line 3: [[size larger]] **...** [[/size]]
            var span3 = document.createElement('span');
            span3.style.fontSize = 'larger';
            var strong2 = document.createElement('strong');
            strong2.textContent = '无#/XXXX级权限下访问将被记录并立即处以纪律处分。';
            span3.appendChild(strong2);
            centerDiv.appendChild(span3);
            
            divContent.appendChild(centerDiv);
            divBox.appendChild(divContent);
            
            // Insert or Replace
            if (comp) {{
                if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                    comp.parentNode.replaceChild(divBox, comp);
                }} else {{
                    comp.parentNode.insertBefore(divBox, comp.nextSibling);
                }}
            }} else {{
                editor.appendChild(divBox);
            }}
            
            // Ensure space after
            var br = document.createElement('br');
            if (divBox.nextSibling) {{
                divBox.parentNode.insertBefore(br, divBox.nextSibling);
            }} else {{
                divBox.parentNode.appendChild(br);
            }}
            
        }})();
        """
        self.browser.page().runJavaScript(js)


    def apply_o5_command(self, pos):
        # Create O5 Command Box
        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component, .acs-box, .rate-module-box, .tabview-box, .collapsible-box, .license-box, .wikidot-table, .div-box, .css-box, .raisa-box, .class-warning-box, .o5-box') : null;
            
            // Create Outer Box
            var divBox = document.createElement('div');
            divBox.className = 'scp-component o5-box'; 
            divBox.setAttribute('data-type', 'o5-command');
            divBox.setAttribute('contenteditable', 'false');
            
            var style = "background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px;";
            divBox.style.cssText = style + " position: relative; clear: both;";
            
            // Create Content Container
            var divContent = document.createElement('div');
            divContent.className = 'o5-content';
            divContent.setAttribute('contenteditable', 'true');
            
            // 4 Empty lines at top
            for(let i=0; i<4; i++) {{
                let p = document.createElement('p');
                p.innerHTML = '<br>'; 
                divContent.appendChild(p);
            }}
            
            // Centered Block
            var centerDiv = document.createElement('div');
            centerDiv.style.textAlign = 'center';
            centerDiv.className = 'o5-center-block';
            
            // Line 1: ++* ##black|...##
            var h2 = document.createElement('h2');
            h2.style.margin = '0';
            var span1 = document.createElement('span');
            span1.style.color = 'black';
            var strong1 = document.createElement('strong');
            strong1.textContent = '根据监督者议会的命令';
            span1.appendChild(strong1);
            h2.appendChild(span1);
            centerDiv.appendChild(h2);
            
            // Line 2: ##black|...##
            var p2 = document.createElement('p');
            var span2 = document.createElement('span');
            span2.style.color = 'black';
            span2.textContent = '以下文件为X/XXXX级机密。禁止未经授权的访问。';
            p2.appendChild(span2);
            centerDiv.appendChild(p2);
            
            divContent.appendChild(centerDiv);
            
            // Line 3: = **##black|XXXX##**
            var h1 = document.createElement('h1');
            h1.style.textAlign = 'center';
            var span3 = document.createElement('span');
            span3.style.color = 'black';
            var strong3 = document.createElement('strong');
            strong3.textContent = 'XXXX';
            span3.appendChild(strong3);
            h1.appendChild(span3);
            divContent.appendChild(h1);
            
            // 2 Empty lines at bottom
            for(let i=0; i<2; i++) {{
                 let p = document.createElement('p');
                 p.innerHTML = '<br>';
                 divContent.appendChild(p);
            }}

            divBox.appendChild(divContent);
            
            // Insert or Replace
            if (comp) {{
                if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                    comp.parentNode.replaceChild(divBox, comp);
                }} else {{
                    comp.parentNode.insertBefore(divBox, comp.nextSibling);
                }}
            }} else {{
                editor.appendChild(divBox);
            }}
            
            // Space after
            var br = document.createElement('br');
            if (divBox.nextSibling) {{
                divBox.parentNode.insertBefore(br, divBox.nextSibling);
            }} else {{
                divBox.parentNode.appendChild(br);
            }}
            
        }})();
        """
        self.browser.page().runJavaScript(js)

    def apply_video_record(self, pos):
        """Insert Video/Audio Record Div (class='blockquote', no special rendering)"""
        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component') : null;

            // Build the div-box exactly like a standard div block
            var divBox = document.createElement('div');
            divBox.className = 'scp-component div-box';
            divBox.setAttribute('data-type', 'div-block');
            divBox.setAttribute('contenteditable', 'false');
            divBox.style.cssText = 'position: relative; clear: both;';

            // Collapsible header (matches normal div-box pattern)
            var divHeader = document.createElement('div');
            divHeader.className = 'div-header';
            divHeader.setAttribute('contenteditable', 'true');
            divHeader.setAttribute('onclick', 'toggleDiv(this)');
            divHeader.style.cssText = 'cursor:pointer;';
            divHeader.title = '点击折叠/展开';
            divHeader.textContent = 'DIV: class="blockquote"';
            divBox.appendChild(divHeader);

            // Content area with template
            var divContent = document.createElement('div');
            divContent.className = 'div-content';
            divContent.setAttribute('contenteditable', 'true');
            divContent.innerHTML = [
                '<div style="text-align:center;"><b>\u89c6\u9891\u8bb0\u5f55</b></div>',
                '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
                '<p><b>\u65e5\u671f\uff1a</b></p>',
                '<p><b>\u7b14\u8bb0\uff1a</b></p>',
                '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
                '<p>[\u8bb0\u5f55\u5f00\u59cb]</p>',
                '<p><b>\u65f6\u95f4\uff1a</b>\u4e8b\u4ef6</p>',
                '<p><b>\u65f6\u95f4\uff1a</b>\u4e8b\u4ef6</p>',
                '<p><b>\u65f6\u95f4\uff1a</b>\u4e8b\u4ef6</p>',
                '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
                '<p>[\u8bb0\u5f55\u7ed3\u675f]</p>'
            ].join('');
            divBox.appendChild(divContent);

            // Insert or Replace
            if (comp) {{
                if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                    comp.parentNode.replaceChild(divBox, comp);
                }} else {{
                    comp.parentNode.insertBefore(divBox, comp.nextSibling);
                }}
            }} else {{
                editor.appendChild(divBox);
            }}

            var br = document.createElement('br');
            if (divBox.nextSibling) {{
                divBox.parentNode.insertBefore(br, divBox.nextSibling);
            }} else {{
                divBox.parentNode.appendChild(br);
            }}
        }})();
        """
        self.browser.page().runJavaScript(js)

    def apply_video_record2(self, pos):
        """Insert Video/Audio Record v2 - detailed exploration log format"""
        params = 'class="blockquote" style="border-radius: 10px; margin: 10px"'
        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component') : null;

            var divBox = document.createElement('div');
            divBox.className = 'scp-component div-box';
            divBox.setAttribute('data-type', 'div-block');
            divBox.setAttribute('contenteditable', 'false');
            divBox.style.cssText = 'border-radius: 10px; margin: 10px; position: relative; clear: both;';

            var divHeader = document.createElement('div');
            divHeader.className = 'div-header';
            divHeader.setAttribute('contenteditable', 'true');
            divHeader.setAttribute('onclick', 'toggleDiv(this)');
            divHeader.style.cssText = 'cursor:pointer;';
            divHeader.title = '\u70b9\u51fb\u6298\u53e0/\u5c55\u5f00';
            divHeader.textContent = 'DIV: {params}';
            divBox.appendChild(divHeader);

            var divContent = document.createElement('div');
            divContent.className = 'div-content';
            divContent.setAttribute('contenteditable', 'true');
            divContent.innerHTML = [
                '<p><b>\u89c6\u9891\u65e5\u5fd7\u8bb0\u5f55</b></p>',
                '<p><b>\u65e5\u671f\uff1a</b>\u53ef\u9009</p>',
                '<p><b>\u63a2\u7d22\u961f\u4f0d\uff1a</b>\u961f\u4f0d\u540d\u79f0 - \u53ef\u9009</p>',
                '<p><b>\u76ee\u6807\uff1a</b>\u533a\u57df/\u5f02\u5e38 - \u53ef\u9009</p>',
                '<p><b>\u9886\u961f\uff1a</b>\u53ef\u9009</p>',
                '<p><b>\u5c0f\u961f\u6210\u5458\uff1a</b>\u53ef\u9009</p>',
                '<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>',
                '<p>[\u8bb0\u5f55\u5f00\u59cb]</p>',
                '<p><b>\u4eba\u7269A\uff1a</b>\u5bf9\u767d</p>',
                '<p><b>\u4eba\u7269B\uff1a</b>\u5bf9\u767d</p>',
                '<p><i>\u4e8b\u4ef6\u53d1\u751f</i></p>',
                '<p><b>\u4eba\u7269A\uff1a</b>\u5bf9\u767d</p>',
                '<p>[\u8bb0\u5f55\u7ed3\u675f]</p>'
            ].join('');
            divBox.appendChild(divContent);

            if (comp) {{
                if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                    comp.parentNode.replaceChild(divBox, comp);
                }} else {{
                    comp.parentNode.insertBefore(divBox, comp.nextSibling);
                }}
            }} else {{
                editor.appendChild(divBox);
            }}

            var br = document.createElement('br');
            if (divBox.nextSibling) {{
                divBox.parentNode.insertBefore(br, divBox.nextSibling);
            }} else {{
                divBox.parentNode.appendChild(br);
            }}
        }})();
        """
        self.browser.page().runJavaScript(js)

    def apply_page_note(self, pos):
        """Insert Page Note (便签纸) component - lined paper style."""
        page_style = (
            'display:block; overflow:hidden; '
            'font-family:"Monotype Corsiva","Bradley Hand ITC",sans-serif; '
            'background-attachment:scroll; '
            'background-image:linear-gradient(to top,rgb(202,219,228) 0%,rgb(231,233,220) 8%); '
            'background-position:0px 8px; background-repeat:repeat; background-size:100% 20px; '
            'border:1px solid #CCC; border-radius:10px; padding:10px; margin-bottom:10px; '
            'box-shadow:0px 1px 3px rgba(0,0,0,0.2); position:relative; clear:both;'
        )
        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component') : null;

            var box = document.createElement('div');
            box.className = 'scp-component page-note-box';
            box.setAttribute('data-type', 'page-note');
            box.setAttribute('contenteditable', 'false');
            box.style.cssText = '{page_style}';

            var label = document.createElement('div');
            label.className = 'page-note-label';
            label.setAttribute('contenteditable', 'false');
            label.style.cssText = 'font-size:10px;color:#aaa;text-align:right;margin-bottom:2px;';
            label.textContent = '\u4fbf\u7b7e\u7eb8';
            box.appendChild(label);

            var content = document.createElement('div');
            content.className = 'page-note-content';
            content.setAttribute('contenteditable', 'true');
            content.style.cssText = "font-family:'Monotype Corsiva','Bradley Hand ITC',sans-serif;line-height:20px;";
            content.innerHTML = [
                '<p>\u6b63\u6587\u5728\u6b64\u3002</p>',
                '<p><br></p>',
                '<p>\u5c31\u50cf\u8fd9\u6837\u3002</p>'
            ].join('');
            box.appendChild(content);

            if (comp) {{
                if (comp.classList.contains('div-box') || comp.classList.contains('css-box')) {{
                    comp.parentNode.replaceChild(box, comp);
                }} else {{
                    comp.parentNode.insertBefore(box, comp.nextSibling);
                }}
            }} else {{
                editor.appendChild(box);
            }}

            var br = document.createElement('br');
            if (box.nextSibling) {{
                box.parentNode.insertBefore(br, box.nextSibling);
            }} else {{
                box.parentNode.appendChild(br);
            }}
        }})();
        """
        self.browser.page().runJavaScript(js)

    def apply_login_logout(self, pos):
        """Insert Login/Logout (登入/登出) component."""
        js = f"""
        (function() {{
            var editor = document.getElementById('editor-root');
            var el = document.elementFromPoint({pos.x()}, {pos.y()});
            var comp = el ? el.closest('.scp-component') : null;

            // ── Outer wrapper ──
            var box = document.createElement('div');
            box.className = 'scp-component login-logout-box';
            box.setAttribute('data-type', 'login-logout');
            box.setAttribute('contenteditable', 'false');
            box.style.cssText = 'border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;';

            // ── Form table (ID + password + button) ──
            var tbl = document.createElement('table');
            tbl.className = 'login-form-table';
            tbl.setAttribute('contenteditable', 'false');
            tbl.style.cssText = 'margin:0.5em auto; border-collapse:collapse;';

            // Row: ID
            var tr1 = document.createElement('tr');
            var td1a = document.createElement('td');
            td1a.style.cssText = 'width:80px; padding:4px 8px; font-family:sans-serif;';
            td1a.setAttribute('contenteditable', 'false');
            td1a.textContent = 'ID';
            var td1b = document.createElement('td');
            var idInput = document.createElement('span');
            idInput.className = 'login-id-value';
            idInput.setAttribute('contenteditable', 'true');
            idInput.style.cssText = 'display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;';
            idInput.textContent = '\u4f60\u7684ID';
            td1b.appendChild(idInput);
            tr1.appendChild(td1a); tr1.appendChild(td1b);

            // Row: 密码
            var tr2 = document.createElement('tr');
            var td2a = document.createElement('td');
            td2a.style.cssText = 'width:80px; padding:4px 8px; font-family:sans-serif;';
            td2a.setAttribute('contenteditable', 'false');
            td2a.textContent = '\u5bc6\u7801';
            var td2b = document.createElement('td');
            var pwSpan = document.createElement('span');
            pwSpan.setAttribute('contenteditable', 'false');
            pwSpan.style.cssText = 'display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif; color:#555; letter-spacing:2px;';
            pwSpan.textContent = '\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb';
            td2b.appendChild(pwSpan);
            tr2.appendChild(td2a); tr2.appendChild(td2b);

            // Row: 登入 button
            var tr3 = document.createElement('tr');
            var td3a = document.createElement('td');
            td3a.setAttribute('contenteditable', 'false');
            var td3b = document.createElement('td');
            td3b.style.textAlign = 'center';
            td3b.setAttribute('contenteditable', 'false');
            var btn = document.createElement('button');
            btn.setAttribute('contenteditable', 'false');
            btn.style.cssText = 'padding:2px 18px; border:1px solid #aaa; background:#f4f4f4; cursor:pointer; font-family:sans-serif;';
            btn.textContent = '\u767b\u5165';
            td3b.appendChild(btn);
            tr3.appendChild(td3a); tr3.appendChild(td3b);

            tbl.appendChild(tr1); tbl.appendChild(tr2); tbl.appendChild(tr3);
            box.appendChild(tbl);

            // ── Separator ──
            var sep = document.createElement('hr');
            sep.setAttribute('contenteditable', 'false');
            sep.style.cssText = 'border:none; border-top:1px solid #ccc; margin:6px 0;';
            box.appendChild(sep);

            // ── Collapsible label ──
            var lbl = document.createElement('div');
            lbl.setAttribute('contenteditable', 'false');
            lbl.style.cssText = 'font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;';
            lbl.textContent = '[\u767b\u5165]\u2194[\u767b\u51fa] \u6298\u53e0\u5185\u5bb9';
            box.appendChild(lbl);

            // ── Collapsible content (editable) ──
            var content = document.createElement('div');
            content.className = 'login-collapsible-content';
            content.setAttribute('contenteditable', 'true');
            content.style.cssText = 'min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;';
            content.innerHTML = '<p>\u6587\u5b57</p>';
            box.appendChild(content);

            // ── Insert ──
            if (comp) {{
                comp.parentNode.insertBefore(box, comp.nextSibling);
            }} else {{
                editor.appendChild(box);
            }}
            var br = document.createElement('br');
            box.parentNode.insertBefore(br, box.nextSibling);
        }})();
        """
        self.browser.page().runJavaScript(js)

    def change_acs_class(self, pos, class_name):
        self.browser.page().runJavaScript(
            f'applyAcsChange(document.elementFromPoint({pos.x()}, {pos.y()}), "{class_name}")')

    def change_acs_secondary(self, pos, class_name):
        val = class_name if class_name != "None" else "none"
        self.browser.page().runJavaScript(
            f'applyAcsSecondary(document.elementFromPoint({pos.x()}, {pos.y()}), "{val}")')

    def edit_footnote_at_pos(self, pos):
        js = f"var el = document.elementFromPoint({pos.x()}, {pos.y()}); while(el && !el.classList.contains('scp-footnote')) el = el.parentElement; el ? el.getAttribute('data-content') : ''"

        def on_got(content):
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑脚注", "内容:", content)
            if ok: self.browser.page().runJavaScript(
                f"var el = document.elementFromPoint({pos.x()}, {pos.y()}); while(el && !el.classList.contains('scp-footnote')) el = el.parentElement; if(el) {{ el.setAttribute('data-content', {json.dumps(new_text)}); refreshFootnotes(); }}")

    def open_footnote_editor(self, index):
        """Called via CustomWebPage when a footnote is clicked"""
        # We need to get current content first. 
        # Since we have the index, we can target it directly via JS.
        js = f"document.querySelectorAll('.scp-footnote')[{index}].getAttribute('data-content')"
        
        def on_got(content):
            if content is None: content = ""
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑脚注", "内容:", content)
            if ok:
                # Update content and title
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


    def open_license_link_editor(self, element_id):
        """Called via CustomWebPage when a license source link is clicked"""
        # Get current text
        js = f"document.getElementById('{element_id}').innerText"
        
        def on_got_link(content):
            if content is None: content = ""
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑来源链接", "请输入链接地址:", content)
            if ok:
                # Update text
                update_js = f"""
                (function(){{
                    var el = document.getElementById('{element_id}');
                    if(el) {{
                        el.innerText = {json.dumps(new_text)};
                    }}
                }})()
                """
                self.browser.page().runJavaScript(update_js)
        
        self.browser.page().runJavaScript(js, on_got_link)

    def remove_component_at_pos(self, pos):
        self.browser.page().runJavaScript(
            f"var el = document.elementFromPoint({pos.x()}, {pos.y()}).closest('.scp-component'); if(el) {{ el.remove(); refreshFootnotes(); }}")

    def export_wikidot(self):
        js_sync = "document.querySelectorAll('.acs-anim-checkbox').forEach(cb => {{ if(cb.checked) cb.setAttribute('checked', 'checked'); else cb.removeAttribute('checked'); }});"
        self.browser.page().runJavaScript(js_sync)
        self.browser.page().toHtml(self.process_html)

    def parse_node(self, node, state):
        # 安全获取属性值的辅助函数
        def safe_get(selector, attr='text'):
            el = node.select_one(selector)
            if not el:
                return ""
            if attr == 'text':
                return el.get_text().strip()
            return el.get(attr, "").strip()

        if isinstance(node, NavigableString): return str(node)

        # 修复：遍历所有子节点，以支持嵌套在 tbody/thead 中的行
        if node.name == 'table':
            lines = []

            # 使用 BS4 children 迭代，如果是 tbody/thead 则进一步提取 tr
            all_rows = []
            for child in node.children:
                if child.name == 'tr':
                    all_rows.append(child)
                elif child.name in ['tbody', 'thead', 'tfoot']:
                    all_rows.extend(child.find_all('tr', recursive=False))

            for tr in all_rows:
                line_parts = []
                for cell in tr.find_all(['td', 'th'], recursive=False):
                    colspan = int(cell.get('colspan', '1'))
                    prefix = "||" * colspan
                    content = "".join(self.parse_node(c, state) for c in cell.contents).strip()
                    content = content.replace('\n', ' _\n')  # Wikidot line break in cell

                    if cell.name == 'th':
                        prefix += "~ "
                    else:
                        prefix += " "

                    line_parts.append(f"{prefix}{content}")
                lines.append(" ".join(line_parts) + " ||")  # End the row
            return "\n" + "\n".join(lines) + "\n"

        if node.get('class') and 'scp-component' in node.get('class'):
            c_type = node.get('data-type')

            if c_type == 'theme-basalt':
                return ""

            if c_type == 'aim':
                f = lambda d: safe_get(f'[data-field="{d}"]')
                blocks = node.get('data-blocks', '')
                code = "[[include :scp-wiki-cn:component:advanced-information-methodology\n"
                if blocks: code += f"|blocks={blocks}\n"
                code += "|lang=CN\n"
                # Export Logic Correction:
                # blocks=! -> Hide Top -> Exclude Top Fields if blocks=='!'
                if blocks != '!':
                    code += f"|XXXX={f('xxxx')}\n|lv={f('lv')}\n|cc={f('cc')}\n|dc={f('dc')}\n"
                # blocks=- -> Hide Bottom -> Exclude Bottom Fields if blocks=='-'
                if blocks != '-':
                    code += f"|site={f('site')}\n|dir={f('dir')}\n|head={f('head')}\n|mtf={f('mtf')}\n"
                code += "]]\n"
                return code

            if c_type == 'image-block':
                name = safe_get('[data-field="name"]')
                caption = safe_get('[data-field="caption"]')
                align = node.get('data-align', 'center')
                align_param = ""
                if align == 'left': align_param = "|align=left"
                if align == 'right': align_param = "|align=right"

                return f"[[include component:image-block name={name} |caption={caption}{align_param}]]\n"

            if c_type == 'image-block-adv':
                name = safe_get('[data-field="name"]')
                caption = safe_get('[data-field="caption"]')
                width = safe_get('[data-field="width"]')
                height = safe_get('[data-field="height"]')
                align = node.get('data-align', 'right')  # Default right per prompt request for buttons

                params = f"| name={name}\n| caption={caption}"
                if width:
                    width_val = width.lower().replace('px', '')
                    params += f"\n| width={width_val}px"
                if height:
                    height_val = height.lower().replace('px', '')
                    params += f"\n| height={height_val}px"
                if align in ['left', 'right']: params += f"\n| align={align}"

                return f"[[include component:image-block\n{params}]]\n"

            if c_type == 'tabview':
                buttons = node.select('.tab-header .tab-btn')
                contents = node.select('.tab-contents .tab-item')

                code = "\n[[tabview]]\n"
                for i, btn in enumerate(buttons):
                    title = btn.get_text().strip()
                    if i < len(contents):
                        # Recursive parsing for content
                        tab_body = "".join(self.parse_node(c, state) for c in contents[i].contents).strip()
                        code += f"[[tab {title}]]\n{tab_body}\n[[/tab]]\n"
                code += "[[/tabview]]\n"
                return code

            if c_type == 'user':
                username = safe_get('.user-name')
                return f"[[user {username}]]"

            if c_type == 'user-adv':
                username = safe_get('.user-name')
                return f"[[*user {username}]]"

            if c_type == 'collapsible':
                show_t = safe_get('[data-field="show"]')
                hide_t = safe_get('[data-field="hide"]')
                inner = "".join(
                    self.parse_node(c, state) for c in node.select_one('.collapsible-content-area').contents)
                return f'\n[[collapsible show="{show_t}" hide="{hide_t}"]]\n{inner.strip()}\n[[/collapsible]]\n'

            if c_type == 'license':
                # License parsing logic handled via extraction in process_html
                # Here we return empty to not duplicate it in body
                return ""

            if c_type == 'acs':
                item = safe_get('[data-field="item-number"]')
                clr = (re.search(r'\d+', safe_get('[data-field="clearance"]')) or re.search(r'\d+', '1')).group()

                # Check for secondary
                sec = safe_get('[data-field="secondary"]').lower()
                if sec == "none": sec = ""

                # Logic: If secondary is present, force container class to "esoteric" (机密) in generated code
                # The prompt says: "if use secondary class, automatically change container class to esoteric (change english 'esoteric' to Chinese '机密')"
                cnt_raw = safe_get('[data-field="container"]').lower()
                if sec:
                    cnt = '机密'
                else:
                    cnt = cnt_raw

                dsr = safe_get('[data-field="disruption"]').lower()
                rsk = safe_get('[data-field="risk"]').lower()

                anim = ""
                checkbox = node.select_one('.acs-anim-checkbox')
                if checkbox and checkbox.has_attr('checked'):
                    anim = "[[include :scp-wiki-cn:component:acs-animation]]\n"

                sec_line = ""
                if sec:
                    sec_line = f"|secondary-class={sec}\n"
                    # Add secondary icon if present
                    sec_icon = safe_get('[data-field="secondary-icon"]')
                    if sec_icon:
                        sec_line += f"|secondary-icon={sec_icon}\n"

                return f"\n{anim}[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number={item}\n|clearance={clr}\n|container-class={cnt}\n{sec_line}|disruption-class={dsr}\n|risk-class={rsk}\n]]\n"

            if c_type == 'toc':
                return "\n[[toc]]\n"

            if c_type == 'footnote':
                content = node.get('data-content', '').strip()
                if state.get('better_footnotes', False):
                    return f'[[span class="fnnum"]].[[/span]][[span class="fncon"]]{content}[[/span]]'
                else:
                    return f" [[footnote]] {content} [[/footnote]] "

            if c_type == 'hr': return "\n------\n"

            if c_type == 'raisa-notice':
                # Custom Export for WYSIWYG Raisa Box
                style = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5;"
                inner = "".join(self.parse_node(c, state) for c in node.select_one('.raisa-content').contents).strip()
                return f"\n[[div style=\"{style}\"]]\n{inner}\n[[/div]]\n"

            if c_type == 'class-warning':
                style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) bottom right no-repeat; border: solid 2px black; padding: 0 20px 20px 20px; margin: 10px auto; width: fit-content; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"
                inner = "".join(self.parse_node(c, state) for c in node.select_one('.class-warning-content > .class-warning-inner').contents).strip()
                # The prompt asks for [[=]] wrap as well.
                # Since inner content was centered via text-align center in DOM, parse_node recursion might have added [[=]] if it saw the div?
                # But here we select contents of inner div.
                # We should explicitly wrap in [[=]] and [[div]] as requested.
                return f"\n[[=]]\n[[div style=\"{style}\"]]\n{inner}\n[[/div]]\n[[/=]]\n"

            if c_type == 'o5-command':
                style = "background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px;"
                # Inner content parsing
                # We need to ensure @@@@ are generated.
                # If we parse recursively, empty p-tags might be parsed as newlines or ignored.
                # We can try standard recursion first.
                # However, the user explicitly asked for "@@@@".
                # Standard parsing of <p><br></p> might give "\n" or nothing depending on implementation.
                # Let's customize it or rely on a helper if needed. 
                # Actually, our `parse_node` has logic for 'p' tag with 'br' -> "\n@@@@\n" (lines 2960-2961 in viewed code earlier).
                # Re-checking that logic.
                # Yes: if tag == 'p' and not content.strip() and node.find('br'): return "\n@@@@\n"
                # So standard recursion should work if DOM structure matches!
                
                inner = "".join(self.parse_node(c, state) for c in node.select_one('.o5-content').contents).strip()
                return f"\n[[div style=\"{style}\"]]\n{inner}\n[[/div]]\n"

            if c_type == 'page-note':
                PAGE_CSS = (
                    '[[module CSS]]\n'
                    '.page {\n'
                    '    display: block;\n'
                    '    overflow: hidden;\n'
                    '    font-family: "Monotype Corsiva", "Bradley Hand ITC", sans-serif;\n'
                    '    font-style: normal;\n\n'
                    '    background-attachment: scroll;\n'
                    '    background-clip: border-box;\n'
                    '    background-color: transparent;\n'
                    '    background-image: linear-gradient(to top ,rgb(202, 219, 228) 0%, rgb(231, 233, 220) 8%);\n'
                    '    background-origin: padding-box;\n'
                    '    background-position: 0px 8px;\n'
                    '    background-repeat: repeat;\n'
                    '    background-size: 100% 20px;\n\n'
                    '    border: 1px solid #CCC;\n'
                    '    border-radius: 10px;\n'
                    '    padding: 10px 10px;\n'
                    '    margin-bottom: 10px;\n\n'
                    '    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.2)\n'
                    '    }\n'
                    '.page p,\n'
                    '.page ul {\n'
                    '    line-height: 20px;\n'
                    '    margin: 0;\n'
                    '}\n'
                    '[[/module]]'
                )
                content_node = node.select_one('.page-note-content')
                inner = ''.join(self.parse_node(c, state) for c in content_node.contents).strip() if content_node else ''
                return f"\n{PAGE_CSS}\n[[div class=\"page\"]]\n{inner}\n[[/div]]\n"

            if c_type == 'login-logout':
                FAKEPROT_CSS = (
                    '[[module CSS]]\n'
                    '.fakeprot .mailform-box .buttons{display:none;}\n'
                    '.fakeprot + .collapsible-block .collapsible-block-link {padding: 0.1em 0.5em;'
                    'text-decoration: none;background-color: #F4F4F4;border: 1px solid #AAA;color: #000;}\n'
                    '.fakeprot + .collapsible-block .collapsible-block-link:hover {background-color: #DDD;color: #000;}\n'
                    '.fakeprot + .collapsible-block .collapsible-block-link:active {background-color: #DDD;color: #000;}\n'
                    '.fakeprot + .collapsible-block .collapsible-block-unfolded-link{margin:0.5em 0;text-align: center;}\n'
                    '.fakeprot + .collapsible-block .collapsible-block-folded{margin:0.5em 0;text-align: center;}\n'
                    '.fakeprot .passw input[type=text] {text-security:disc;-webkit-text-security:disc;-mox-text-security:disc;}\n'
                    '.mailform-box td:first-child {width: 80px;}\n'
                    '[[/module]]'
                )
                # Get the editable ID default value
                id_val_node = node.select_one('.login-id-value')
                id_val = id_val_node.get_text().strip() if id_val_node else '你的ID'
                # Get collapsible inner content
                coll_node = node.select_one('.login-collapsible-content')
                coll_inner = ''.join(self.parse_node(c, state) for c in coll_node.contents).strip() if coll_node else '文字'
                fakeprot_block = (
                    '[[div class="fakeprot"]]\n'
                    '[[module MailForm to="aaaa (DUMMY)" button=""]]\n'
                    '# name\n'
                    ' * title: ID\n'
                    f' * default: <{id_val}>\n'
                    ' * type: text\n'
                    ' * rules:\n'
                    '  * required: true\n'
                    '  * maxLength:10\n'
                    '  * minLength: 100\n'
                    '[[/module]]\n'
                    '[[div class="passw"]]\n'
                    '[[module MailForm to="aaaa (DUMMY)" button=""]]\n'
                    '# affiliation\n'
                    ' * title: 密码\n'
                    ' * default: ・・・・・・・・・\n'
                    ' * rules:\n'
                    '  * required: true\n'
                    '  * maxLength:10\n'
                    '  * minLength: 100\n'
                    '[[/module]]\n'
                    '[[/div]]\n'
                    '[[/div]]\n'
                    f'[[collapsible show="登入" hide="登出"]]\n'
                    f'{coll_inner}\n'
                    '[[/collapsible]]'
                )
                return f'\n{FAKEPROT_CSS}\n{fakeprot_block}\n'

            if c_type == 'div-block':
                params = safe_get('.div-header', 'text').replace('DIV:', '').strip()
                inner = "".join(self.parse_node(c, state) for c in node.select_one('.div-content').contents).strip()
                return f"\n[[div {params}]]\n{inner}\n[[/div]]\n"


            if c_type == 'css-module':
                css_code = safe_get('.css-content', 'text').strip()
                return f"\n[[module CSS]]\n{css_code}\n[[/module]]\n"

        # 处理表格导出
        # (Already handled above for standard HTML tables, but kept for fallback or if nested logic needs it)
        # Note: The 'if node.name == table' block at start of function is primary.

        # 递归处理子节点
        content = "".join(self.parse_node(child, state) for child in node.contents)
        tag = node.name

        # --- 强制换行符逻辑 ---
        if tag == 'p' and not content.strip() and node.find('br'):
            return "@@@@\n"

        # Check for alignment style
        style = node.get('style', '') if hasattr(node, 'get') else ''
        align_mark = ""
        if 'text-align: right' in style or 'text-align:right' in style:
            align_mark = ">"
        elif 'text-align: left' in style or 'text-align:left' in style:
            align_mark = "<"
        elif 'text-align: center' in style or 'text-align:center' in style:
            align_mark = "="

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            return f"\n{'+' * level} {content.strip()}\n"

        # --- Custom Dash Export Fix (MUST be before style check - span has no style) ---
        if tag == 'span' and 'custom-dash' in node.get('class', []):
            count = node.get('data-count', '6')
            try:
                count = int(count)
            except ValueError:
                count = 6
            return f'@{"-" * count}@'

        # --- 修复：span 标签样式解析 ---
        if tag == 'span' and node.has_attr('style'):
            if 'monospace' in style or 'Courier' in style:
                return f"{{{{{content}}}}}"

            res = content

            # 解析颜色
            color_match = re.search(r'color:\s*([^;]+)', style)
            if color_match:
                color_val = color_match.group(1).strip()
                # 兼容 rgb(r, g, b) 或 hex
                res = f"##{color_val}|{res}##"

            # 解析字号
            size_match = re.search(r'font-size:\s*([\w\.\-%]+)', style)
            if size_match:
                size_val = size_match.group(1).strip()
                res = f"[[size {size_val}]]{res}[[/size]]"

            return res

        # New relative font size parsing support with %
        # (This was already integrated in previous step, ensuring regex is correct)
        size_match = re.search(r'font-size:\s*([\w\.\-%]+)', style)
        if tag == 'span' and size_match:
            # Already handled above, this is just double checking if missed
            pass

        # Handle font tag (generated by execCommand sometimes)
        if tag == 'font':
            res = content
            if node.has_attr('color'):
                res = f"##{node['color']}|{res}##"
            if node.has_attr('size'):
                # font size attribute is 1-7, mapping roughly or ignore?
                pass
            return res

        if tag == 'sup': return f"^^ {content} ^^"
        if tag == 'sub': return f",, {content} ,,"

        # Lists
        if tag == 'li':
            parent = node.parent
            if parent.name == 'ul':
                return f"* {content.strip()}\n"
            elif parent.name == 'ol':
                return f"# {content.strip()}\n"
            return f"* {content.strip()}\n"

        if tag == 'blockquote':
            lines = content.split('\n')
            res = ""
            for line in lines:
                # Export all lines including empty ones to preserve structure
                res += f"> {line}\n"
            return res + "\n"

        # Handle 'a' tags for links
        if tag == 'a':
            href = node.get('href')
            text = content.strip()
            target = node.get('target')

            # Wikidot syntax based on user's image request:
            # [[[url | text]]] for standard link
            # [[[ *url | text ]]] for new window link

            prefix = ""
            if target == '_blank':
                prefix = "*"

            return f"[{prefix}{href} {text}]"

        # Fixed P tag handling to remove extra leading newline
        if tag == 'p':
            val = f"{content}\n"
            if align_mark: return f"[[{align_mark}]]\n{content.strip()}\n[[/{align_mark}]]\n"
            return val

        if tag == 'div':
            if align_mark:
                 return f"[[{align_mark}]]\n{content.strip()}\n[[/{align_mark}]]\n"
            
            # Generic DIV handling for nested components (e.g. terminal scanline)
            if node.has_attr('class'):
                cls = " ".join(node['class'])
                # avoid capturing internal editor classes if they leak in, though typically they use div-box
                if 'scp-component' not in cls and 'div-content' not in cls and 'div-header' not in cls:
                    return f"[[div class=\"{cls}\"]]\n{content}\n[[/div]]\n"
            return content

        if tag == 'br': return "\n"
        if tag in ['b', 'strong']: return f"**{content}**"
        if tag in ['i', 'em']: return f"//{content}//"
        return content

    def process_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        # Newline Export Fix: Remove visual symbols before processing
        # (Removed as they are no longer generated)

        root = soup.find(id="editor-root")
        if not root: return

        # 0. 解析评分模块 Rate Module
        rate_box = soup.select_one('.rate-module-box')
        rate_code = ""
        if rate_box:
            is_hidden = rate_box.get('data-hidden') == 'true'
            if not is_hidden:
                align = rate_box.get('data-align', '')
                if align == 'left':
                    rate_code = "[[<]]\n[[module Rate]]\n[[/<]]\n"
                elif align == 'right':
                    rate_code = "[[>]]\n[[module Rate]]\n[[/>]]\n"
                else:
                    rate_code = "[[module Rate]]\n"
            rate_box.decompose() # Ensure it doesn't interfere

        final_code = rate_code

        # 1.5 Detect Rate Module State (rest handled below)
        
        # Check for Terminal Style CSS in the generated code itself?
        # Use simple heuristic: if ".danke" and ".agent" in final_code?
        # Wait, final_code is built here.
        # We should check the DOM or parsed content? 
        # Actually `process_html` parses the DOM placeholders.
        # Let's check if we have any CSS module that looks like Terminal Style.
        
        # We can inspect `soup` before generating code.
        is_terminal = False
        css_modules = soup.select('.css-content')
        for cm in css_modules:
            if '.danke' in cm.text and '.agent' in cm.text:
                is_terminal = True
                break
        
        # 1. 插入全局版式 (基于内部状态，而非DOM)
        self.update_theme_state()

        if not is_terminal: # Only generate themes if NOT terminal style
            if self.page_theme_config["type"] == "basalt":
                options = self.page_theme_config["options"]
                if options:
                    final_code += f"[[include :scp-wiki-cn:theme:basalt 版式设置|{'|'.join(options)}]]\n"
                else:
                    final_code += "[[include :scp-wiki-cn:theme:basalt]]\n"
    
            elif self.page_theme_config["type"] == "shivering":
                suffix = self.page_theme_config.get("shivering_suffix", "")
                final_code += f"[[include :scp-wiki-cn:theme:shivering-night{suffix}]]\n"
    
            elif self.page_theme_config["type"] == "bhl":
                final_code += "[[include :scp-wiki-cn:theme:black-highlighter-theme]]\n"
                bhl_opts = self.page_theme_config.get("bhl_options", {})
                
                if bhl_opts.get("dark_sidebar"):
                    final_code += "[[include :scp-wiki:component:bhl-dark-sidebar]]\n"
                if bhl_opts.get("collapsible"):
                    final_code += "[[include :scp-wiki:component:collapsible-sidebar]]\n"
                if bhl_opts.get("toggle"):
                    final_code += "[[include :scp-wiki:component:toggle-sidebar-bhl]]\n"
                if bhl_opts.get("centered"):
                    final_code += "[[include :scp-wiki:component:centered-header-bhl]]\n"
                if bhl_opts.get("office"):
                    final_code += "[[include :scp-wiki-cn:theme:scp-offices-theme]]\n"
                if bhl_opts.get("raisa"):
                    final_code += "[[include :scp-wiki-cn:theme:raisa-sigma]]\n"
    
            # 1.5 插入暗色侧边栏 (Dark Sidebar) - 紧跟版式代码
            if self.page_theme_config.get("dark_sidebar", False):
                final_code += "[[include :scp-wiki:component:bhl-dark-sidebar]]\n"
        
        # If terminal, we might want to ensure themes are unchecked in UI?
        # But process_html is for export. 
        # The prompt says "cancel layout rendering and code generation".
        # We skipped generation above.
        
        # 2. 插入 Better Footnotes


        # 2. 插入 Better Footnotes
        if self.use_better_footnotes:
            final_code += "[[include :scp-wiki-cn:component:betterfootnotes]]\n"

        # 3. 准备解析状态
        parse_state = {'better_footnotes': self.use_better_footnotes}

        # Helper to extract and parse specific components
        def extract_and_parse(selector_dict):
            components = root.find_all(attrs=selector_dict)
            parsed_code = ""
            for comp in components:
                parsed_code += self.parse_node(comp, parse_state)
                comp.decompose()  # Remove from DOM so it doesn't appear in body
            return parsed_code

        # Helper to parse specific license component specifically
        def parse_license_only(comp_node):
            def get_field_lic(n, field):
                el = n.select_one(f'[data-field="{field}"]')
                return el.get_text().strip() if el else ""

            author = get_field_lic(comp_node, "author")
            translator = get_field_lic(comp_node, "translator")

            use_bf = parse_state.get('better_footnotes', False)
            fn_block = "" if use_bf else "[[footnoteblock]]\n"

            base_code = f"{fn_block}[[include :scp-wiki-cn:component:license-box\n|author={author}\n|translator={translator}\n]]\n=====\n"

            files_code = ""
            file_entries = comp_node.select('.file-entry')
            for i, entry in enumerate(file_entries):
                # No intermediate ===== separators.
                # Just separate entries with newlines.
                
                fields = {
                    '文件名': 'file_name',
                    '图像名': 'img_name',
                    '图像作者': 'img_author',
                    '授权协议': 'img_license',
                    '来源链接': 'source_link',
                    '衍生自': 'derived_from',
                    '备注': 'note'
                }
                for label, key in fields.items():
                    val = get_field_lic(entry, key)
                    if val:
                        files_code += f"> **{label}：**{val}\n"
                
                # Add spacing between files, but not after the last one
                if i < len(file_entries) - 1:
                     files_code += "\n"

            return base_code + files_code + "=====\n[[include :scp-wiki-cn:component:license-box-end]]\n"

        # Extract License Box first to append at end
        license_comps = root.find_all(attrs={"data-type": "license"})
        license_code = ""
        for comp in license_comps:
            license_code += parse_license_only(comp)
            comp.decompose()

        # 4. 解析正文 (Natural order)
        raw_body = self.parse_node(root, parse_state)

        # 5. 后处理
        body = raw_body.replace('\r\n', '\n')
        body = re.sub(r'\n{3,}', '\n\n@@@@\n\n', body)

        final_code += body

        # Append license code at the very end
        final_code += license_code

        # New Save Logic handling
        if getattr(self, 'is_saving_mode', False):
            self.is_saving_mode = False  # Reset flag
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
            # Only update display if not saving
            self.source_display.setPlainText(final_code.strip())
            # self.centralWidget().findChild(QTabWidget).setCurrentIndex(1) # Optional: don't auto switch tabs

    def render_to_editor(self):
        """
        反向解析：将源码框的 Wikidot 代码转换为编辑器可视化的 HTML
        """
        code = self.source_display.toPlainText()
        if not code.strip():
            return

        # 1. 解析 Theme/Module 等全局配置 (简单处理)
        # Theme Basalt
        if "theme:basalt" in code:
            self.check_enable_basalt.setChecked(True)
            if "darkmode=a" in code: self.check_dark.setChecked(True)
            if "wide=a" in code: self.check_wide.setChecked(True)
            if "hidetitle=a" in code: self.check_hidetitle.setChecked(True)
            self.on_basalt_toggled(True)
        elif "theme:shivering-night" in code:
            self.check_enable_shivering.setChecked(True)
            # Detect City Sub-themes
            if "theme:shivering-night-macau" in code: self.radio_shiv_mo.setChecked(True)
            elif "theme:shivering-night-kuala-lumpur" in code: self.radio_shiv_kl.setChecked(True)
            elif "theme:shivering-night-dublin" in code: self.radio_shiv_dub.setChecked(True)
            elif "theme:shivering-night-cape-town" in code: self.radio_shiv_ct.setChecked(True)
            elif "theme:shivering-night-buenos-aires" in code: self.radio_shiv_ba.setChecked(True)
            else: self.radio_shiv_default.setChecked(True)
            self.on_shivering_toggled(True)
        elif "theme:black-highlighter-theme" in code:
            self.check_enable_bhl.setChecked(True)
            # Detect BHL Sub-components
            if ":component:bhl-dark-sidebar" in code: self.check_dark_sidebar.setChecked(True)
            if ":component:collapsible-sidebar" in code: self.check_bhl_collapsible.setChecked(True)
            if ":component:toggle-sidebar-bhl" in code: self.check_bhl_toggle.setChecked(True)
            if ":component:centered-header-bhl" in code: self.check_bhl_centered.setChecked(True)
            if "theme:scp-offices-theme" in code: self.check_bhl_office.setChecked(True)
            if "theme:raisa-sigma" in code: self.check_bhl_raisa.setChecked(True)
            self.on_bhl_toggled(True)
        else:
            self.check_enable_basalt.setChecked(False)
            self.check_enable_shivering.setChecked(False)
            self.check_enable_bhl.setChecked(False)
            # Reset sub-options if possible, but unchecked main toggle usually covers it.
            self.on_basalt_toggled(False)

        # Better Footnotes
        if ":component:betterfootnotes" in code:
            self.check_better_footnotes.setChecked(True)
        else:
            self.check_better_footnotes.setChecked(False)
        self.update_theme_state()

        # 1.5 Detect Rate Module State
        rate_hidden = True
        rate_align = ""
        
        # Check standard Rate Module
        if re.search(r'\[\[module Rate\]\]', code, re.IGNORECASE):
            rate_hidden = False
            # Check alignment wrappers
            if re.search(r'\[\[<\]\]\s*\[\[module Rate\]\]\s*\[\[/<\]\]', code, re.IGNORECASE):
                 rate_align = "left"
            elif re.search(r'\[\[>\]\]\s*\[\[module Rate\]\]\s*\[\[/>\]\]', code, re.IGNORECASE):
                 rate_align = "right"

        # 2. 解析正文结构
        html_content = self.parse_wikidot_to_editor_html(code)
        
        # Extract CSS for Live Preview
        extracted_css = ""
        css_matches = re.finditer(r'\[\[module CSS\]\](.*?)\[\[/module\]\]', code, flags=re.DOTALL|re.IGNORECASE)
        for m in css_matches:
            extracted_css += m.group(1).strip() + "\n"
        
        # Termial Style Logic
        if ".danke" in extracted_css and ".agent" in extracted_css:
            # Add Global Terminal Style for ALL div modules
            extracted_css += """
            /* Force Terminal Style for all DIV modules in Editor View */
            /* Force Terminal Style for all DIV modules in Editor View */
            .div-box {
                background-color: #000000 !important;
                border: 2px solid #55AA55 !important;
                color: #77CC77 !important;
                font-family: monospace !important;
            }
            .div-header {
                background-color: #55AA55 !important;
                color: #002200 !important;
                border-bottom: 1px solid #002200 !important;
                font-weight: bold;
            }
            .div-content {
                background-color: #000000 !important;
                color: #77CC77 !important;
            }
            """

        # 3. 注入到 WebView
        # 此时需要转义 HTML 中的引号与换行，以便 JS 执行
        safe_html = html_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        js = f"""
        document.getElementById('editor-root').innerHTML = "{safe_html}";
        
        // Inject Extracted CSS
        var style = document.getElementById('dynamic-terminal-style');
        if (!style) {{
            style = document.createElement('style');
            style.id = 'dynamic-terminal-style';
            document.head.appendChild(style);
        }}
        style.textContent = `{extracted_css.replace('`', '\\`')}`; // Use backticks for multi-line support in JS if possible, or careful replace

        // 重新绑定事件与刷新状态
        if(typeof refreshFootnotes === 'function') refreshFootnotes();
        if(typeof setupObserver === 'function') setupObserver();
        """
        self.browser.page().runJavaScript(js)
        
        
        # 4. 刷新一下 ACS/Tabs 等可能需要的 JS 初始化
        # Tabview 切换逻辑在 onclick，静态 HTML 结构正确即可
        
        # 5. Rate Module State Restoration
        # Using detected state from Step 1 (moved to Step 1 in actual code below)
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
                    
                    // Reset alignment first
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

        QMessageBox.information(self, "渲染完成", "代码已还原到编辑器。(部分复杂格式可能无法完美还原)")

    def parse_wikidot_to_editor_html(self, text):
        """
        核心反向解析器
        输入: Wikidot 源码
        输出: 带有 contenteditable 和编辑器特定 class 的 HTML
        """
        # Placeholder System to protect HTML components from text formatting
        # --- Step 0: HTML Entity Decoding ---
        # The Code View widget HTML-encodes certain characters:
        # [[ becomes &#91;&#91;, ]] becomes &#93;&#93;  (prevents accidental tag interpretation)
        # @@@@ becomes <p><br></p>  (blank paragraph rendering)
        # We must decode these BEFORE any regex matching runs.
        import html as _html_module
        text = _html_module.unescape(text)
        # Convert <p><br></p> patterns (from @@@@) back to plain newlines
        text = re.sub(r'<p>\s*<br\s*/?>\s*</p>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        placeholders = {}
        ph_count = 0
        def register_ph(html_content):
            nonlocal ph_count
            token = f"_WIKIDOT_PH_{ph_count}_"
            placeholders[token] = html_content
            ph_count += 1
            return token

        # 0. Forced Newline (@@@@ -> <br> globally, or specialized?)
        # For Editor: <p><br></p> matches parse_node's export logic for @@@@
        # But we must be careful not to break inline contexts.
        # User requested @@@@ optimization for Terminal #001 specifically.
        
        # New Terminal #001 "Source Mode" Pre-processor
        def process_terminal_source(txt):
            # Find [[div class="terminal"]] ... [[/div]] blocks
            # Since regex is greedy/tricky with nesting, we use a simple scanner for this specific class.
            
            pattern_start = re.compile(r'\[\[div\s+class="terminal"\]\]', re.IGNORECASE)
            pattern_end = re.compile(r'\[\[/div\]\]', re.IGNORECASE)
            
            result = []
            current_pos = 0
            
            # Simple recursive-like structure extraction? 
            # Actually, standard regex replacement with callback is safer if we assume "terminal" div is top-level (or we just handle the content inside).
            # But [[div]]s can be nested.
            # Best approach: Find '[[div class="terminal"]]'. matching '[[/div]]' requires balancing.
            
            # Simplified approach: If we assume terminal div doesn't contain OTHER complex divs that confuse us?
            # Terminal #001 contains nested [[div]]s (scanline, text).
            
            # We will use temporary placeholders for nested divs to isolate the terminal block logic?
            # No, that's complex.
            
            # Let's iterate manually.
            matches = list(pattern_start.finditer(txt))
            if not matches:
                return txt.replace('@@@@', '<br>')
            
            last_end = 0
            new_text = ""
            
            valid_ranges = [] # (start, end)
            
            # Scan for balanced divs starting from each terminal match
            # This is expensive but accurate.
            for m in matches:
                start = m.end()
                bracket_start = m.start()
                if bracket_start < last_end: continue # Nested inside already processed
                
                depth = 1
                search_pos = start
                
                # Scan forward for [[div...]] or [[/div]]
                while depth > 0:
                    next_open = re.search(r'\[\[div.*?\]\]', txt[search_pos:], re.IGNORECASE)
                    next_close = pattern_end.search(txt[search_pos:])
                    
                    if not next_close: # Unbalanced
                        break
                        
                    pos_close = search_pos + next_close.start()
                    pos_open = search_pos + next_open.start() if next_open else -1
                    
                    if next_open and pos_open < pos_close:
                        depth += 1
                        search_pos = pos_open + (next_open.end() - next_open.start())
                    else:
                        depth -= 1
                        search_pos = pos_close + 8 # length of [[/div]]
                        
                if depth == 0:
                    end_content = search_pos - 8 
                    valid_ranges.append((bracket_start, search_pos))
                    last_end = search_pos
            
            # Now reconstruction
            curr = 0
            for start, end in valid_ranges:
                # Add text before
                new_text += txt[curr:start].replace('@@@@', '<br>')
                
                # Process Terminal Block
                raw_block = txt[start:end]
                # Extract content inside [[div class="terminal"]] ... [[/div]]
                # Be careful, raw_block includes the tags.
                # structure: [[div class="terminal"]] CONTENT [[/div]]
                
                # Identify header params
                header_match = pattern_start.match(raw_block)
                header_len = header_match.end()
                footer_len = 8
                
                inner_content = raw_block[header_len:-footer_len]
                
                # --- SOURCE CODE MODE TRANSFORMATION ---
                # 1. Escape Wikidot Components ( [[ -> &#91;&#91; ) so they aren't parsed by later replacers
                #    Except for [[div...]] structure which we might want to keep?
                #    User wants "render source code".
                #    If we escape [[div...]], div_replacer won't find them, and they will render as text.
                #    This is EXACLTY what "render source code" means.
                #    BUT, we want the structure to remain visually?
                #    If we break the div structure, the CSS (.div-box.terminal .div-box) won't apply!
                #    Wait, Terminal CSS relies on nested .div-box structure.
                #    So we MUST parse [[div]]s to HTML divs.
                #    But we must NOT parse [[module]], [[image]], etc.
                
                # Solution: Escape components, but NOT [[div...]].
                
                # Escape function
                def escape_wiki(t):
                    # Escape generic [[ ... ]]
                    # But protect [[div ... ]] and [[/div]]
                    # We can use a temporary placeholder for divs.
                    
                    # 1. Hide divs
                    ph_divs = []
                    def div_hide(m):
                        ph_divs.append(m.group(0))
                        return f"__DIV_PH_{len(ph_divs)-1}__"
                    
                    t = re.sub(r'\[\[/?div.*?\]\]', div_hide, t, flags=re.IGNORECASE)
                    
                    # 2. Escape other [[ ... ]]
                    t = t.replace('[[', '&#91;&#91;').replace(']]', '&#93;&#93;')
                    
                    # 3. Restore divs
                    def div_restore(m):
                        idx = int(m.group(1))
                        return ph_divs[idx]
                    
                    t = re.sub(r'__DIV_PH_(\d+)__', div_restore, t)
                    return t

                processed_inner = escape_wiki(inner_content)
                
                # 2. Handle @@@@ -> <p><br></p> for visual blank line
                processed_inner = processed_inner.replace('@@@@', '<p><br></p>')

                # 3. Handle @@------@@ -> <span class="terminal-hr">------</span> for visual dashes
                processed_inner = processed_inner.replace('@@------@@', '<span class="terminal-hr">------</span>')
                
                # Reassemble
                new_text += raw_block[:header_len] + processed_inner + raw_block[-footer_len:]
                
                curr = end
            
            new_text += txt[curr:].replace('@@@@', '<br>')
            return new_text

        text = process_terminal_source(text)

        # Text pre-cleanup
        
        # 1. Remove Rate Module with alignment wrappers first (so they don't leave empty alignment divs)
        text = re.sub(r'\[\[<\]\]\s*\[\[module Rate\]\]\s*\[\[/<\]\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[>\]\]\s*\[\[module Rate\]\]\s*\[\[/>\]\]', '', text, flags=re.IGNORECASE)
        # 2. Remove remaining Rate Module
        text = re.sub(r'\[\[module Rate\]\]', '', text, flags=re.IGNORECASE)
        
        # remove alignment wrappers for Rate if present (we will assume standard structure or let them be parsed as normal alignment if not matched?)
        # Actually `parse_wikidot_to_editor_html` renders to EDITOR.
        # We need to restore the Rate Module state if we import code.
        # But `rate-module-box` is outside `#editor-root`.
        # So `parse_wikidot_to_editor_html` returns content for `#editor-root`.
        # We need a separate step in `render_to_editor` to handle Rate Module state.
        
        # 移除 theme include, footer, 等
        text = re.sub(r'\[\[include :scp-wiki-cn:theme:basalt.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[include :scp-wiki-cn:theme:shivering-night.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[include :scp-wiki-cn:theme:raisa-sigma.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[include :scp-wiki-cn:theme:black-highlighter-theme.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        
        # Remove BHL Sub-components from text
        text = re.sub(r'\[\[include :scp-wiki:component:bhl-dark-sidebar.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[include :scp-wiki:component:collapsible-sidebar.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[include :scp-wiki:component:toggle-sidebar-bhl.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[include :scp-wiki:component:centered-header-bhl.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[include :scp-wiki-cn:theme:scp-offices-theme.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)

        text = re.sub(r'\[\[include :scp-wiki-cn:component:betterfootnotes.*?\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[\[footnoteblock\]\]\r?\n?', '', text, flags=re.IGNORECASE)
        
        # --- License Box Parser ---
        def license_replacer(match):
            full_block = match.group(0)
            
            # 1. Parse Main Args
            author_m = re.search(r'\|author=([^\|\n\]]+)', full_block)
            translator_m = re.search(r'\|translator=([^\|\n\]]+)', full_block)
            author = author_m.group(1).strip() if author_m else ""
            translator = translator_m.group(1).strip() if translator_m else ""
            
            # 2. Parse Files
            files_content_im = re.search(r'=====(.*?)=====', full_block, flags=re.DOTALL)
            files_html = ""
            
            if files_content_im:
                file_text = files_content_im.group(1).strip()
                lines = file_text.split('\n')
                current_file = {}
                files_data = []
                
                def flush_file():
                    if current_file:
                        files_data.append(current_file.copy())
                        current_file.clear()

                for line in lines:
                    line = line.strip()
                    if not line.startswith('>'): continue
                    content = line[1:].strip()
                    if content.startswith('**文件名：**'):
                        flush_file() # Start new file
                        current_file['file_name'] = content.replace('**文件名：**', '').strip()
                    elif content.startswith('**图像名：**'):
                         current_file['img_name'] = content.replace('**图像名：**', '').strip()
                    elif content.startswith('**图像作者：**'):
                         current_file['img_author'] = content.replace('**图像作者：**', '').strip()
                    elif content.startswith('**授权协议：**'):
                         current_file['img_license'] = content.replace('**授权协议：**', '').strip()
                    elif content.startswith('**来源链接：**'):
                         current_file['source_link'] = content.replace('**来源链接：**', '').strip()
                    elif content.startswith('**衍生自：**'):
                         current_file['derived_from'] = content.replace('**衍生自：**', '').strip()
                    elif content.startswith('**备注：**'):
                         current_file['note'] = content.replace('**备注：**', '').strip()
                
                flush_file() # Flush last
                
                # Build HTML for files
                for f in files_data:
                    files_html += f'<div class="file-entry"><button class="btn-del-file" onclick="this.parentElement.remove()">×</button>'
                    files_html += f'<div class="license-field-row"><span class="field-label">文件名：</span><span class="editable-field" data-field="file_name" contenteditable="true">{f.get("file_name", "")}</span></div>'
                    files_html += f'<div class="license-field-row"><span class="field-label">图像名：</span><span class="editable-field" data-field="img_name" contenteditable="true">{f.get("img_name", "")}</span></div>'
                    files_html += f'<div class="license-field-row"><span class="field-label">图像作者：</span><span class="editable-field" data-field="img_author" contenteditable="true">{f.get("img_author", "")}</span></div>'
                    files_html += f'<div class="license-field-row"><span class="field-label">授权协议：</span><span class="editable-field" data-field="img_license" contenteditable="true">{f.get("img_license", "")}</span></div>'
                    files_html += f'<div class="license-field-row license-link-row"><span class="field-label">来源链接：</span><span class="editable-field" data-field="source_link" contenteditable="false" onclick="editLicenseLink(this)">{f.get("source_link", "")}</span></div>'
                    files_html += f'<div class="license-field-row"><span class="field-label">衍生自：</span><span class="editable-field" data-field="derived_from" contenteditable="true" style="word-break: break-all;">{f.get("derived_from", "")}</span></div>'
                    files_html += f'<div class="license-field-row"><span class="field-label">备注：</span><span class="editable-field" data-field="note" contenteditable="true">{f.get("note", "")}</span></div>'
                    files_html += '</div>'

            html = f'''<div class="scp-component license-box open" data-type="license" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)</div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true">{author}</span></div><div class="license-field-row"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true">{translator}</span></div><hr><div class="extra-files-container">{files_html}</div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>'''
            return register_ph(html)

        text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\].*?\[\[include :scp-wiki-cn:component:license-box-end\]\]', license_replacer, text, flags=re.DOTALL)
        
        text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box-end.*?\]\]', '', text)
        text = re.sub(r'\[\[include :scp-wiki-cn:component:license-box.*?\]\]', '', text, flags=re.DOTALL)
        
        # --- 1. ACS Bar ---
        def acs_replacer(match):
            block = match.group(0)
            def get_arg(name):
                m = re.search(fr'(?:\||\s){name}=([^\|\n\]]+)', block)
                return m.group(1).strip() if m else ""
            
            item = get_arg('item-number')
            clr = get_arg('clearance')
            cnt = get_arg('container-class')
            color_map = {
                'safe': '#27ae60', 'euclid': '#f1c40f', 'keter': '#c0392b',
                'neutralized': '#7f8c8d', 'pending': '#bdc3c7', 
                'explained': '#95a5a6', 'esoteric': '#595959', '机密': '#595959'
            }
            color = color_map.get(cnt.lower(), '#595959')
            sec = get_arg('secondary-class')
            sec_icon = get_arg('secondary-icon')
            dsr = get_arg('disruption-class')
            rsk = get_arg('risk-class')
            anim_checked = 'checked' if 'component:acs-animation' in text else ''
            
            html = f'''<div class="scp-component acs-box" data-type="acs" data-clearance="{clr}" data-container="{cnt}" data-secondary="{sec or 'none'}" data-disruption="{dsr}" data-risk="{rsk}" style="--acs-color: {color};" contenteditable="false"><div class="acs-header-row" contenteditable="false"><div class="acs-title">SCP-CN 异常分级栏</div><div class="acs-anim-toggle"><span>动画:</span><label class="switch"><input type="checkbox" class="acs-anim-checkbox" {anim_checked}><span class="slider"></span></label></div><div class="acs-item-num" contenteditable="true" data-field="item-number">{item}</div></div><div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 10px;"><div><small style="color:#888; font-size:9px; text-transform:uppercase;">许可等级</small><br><b data-field="clearance" contenteditable="true">{clr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">项目等级</small><br><b data-field="container" style="color:var(--acs-color)" contenteditable="true">{cnt}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">次要等级</small><br><b data-field="secondary" contenteditable="true">{sec or "none"}</b><div style="font-size:0.8em; border-top:1px solid #ccc; margin-top:2px;">Icon: <span data-field="secondary-icon" contenteditable="true" style="min-width:20px; display:inline-block">{sec_icon}</span></div></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">扰动等级</small><br><b data-field="disruption" contenteditable="true">{dsr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">风险等级</small><br><b data-field="risk" contenteditable="true">{rsk}</b></div></div></div>'''
            return register_ph(html)

        text = re.sub(r'\[\[include :scp-wiki-cn:component:anomaly-class-bar-source.*?\]\]', acs_replacer, text, flags=re.DOTALL)
        text = re.sub(r'\[\[include :scp-wiki-cn:component:acs-animation\]\]', '', text)

        # --- 2. AIM Module ---
        def aim_replacer(match):
            block = match.group(0)
            def get_arg(name):
                m = re.search(fr'(?:\||\s){name}=([^\|\n\]]+)', block)
                return m.group(1).strip() if m else "???"
            
            blocks_arg = get_arg('blocks')
            # Import Logic Correction:
            # blocks=- : Show Top (Hide Bottom)
            row_style_top = 'display:none;' if blocks_arg == '!' else ''
            # blocks=! : Show Bottom (Hide Top)
            row_style_bottom = 'display:none;' if blocks_arg == '-' else ''
            
            val_xxxx = get_arg('XXXX')
            val_lv = get_arg('lv')
            val_cc = get_arg('cc')
            val_dc = get_arg('dc')
            val_site = get_arg('site')
            val_dir = get_arg('dir')
            val_head = get_arg('head')
            val_mtf = get_arg('mtf')
            
            html = f'''<div class="scp-component aim-box" data-type="aim" data-blocks="{blocks_arg}" contenteditable="false"><table class="aim-table"><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">项目编号</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">{val_xxxx}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">等级 / 公开</div><div class="aim-value" data-field="lv" contenteditable="true">{val_lv}</div></td></tr><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">收容等级</div><div class="aim-value" data-field="cc" contenteditable="true">{val_cc}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">扰动等级</div><div class="aim-value" data-field="dc" contenteditable="true">{val_dc}</div></td></tr><tr style="{row_style_bottom} text-align: center; background: #fafafa;"><td><div class="aim-label">负责站点</div><div class="aim-value" data-field="site" contenteditable="true">{val_site}</div></td><td><div class="aim-label">站点主管</div><div class="aim-value" data-field="dir" contenteditable="true">{val_dir}</div></td><td><div class="aim-label">首席研究员</div><div class="aim-value" data-field="head" contenteditable="true">{val_head}</div></td><td><div class="aim-label">指派特遣队</div><div class="aim-value" data-field="mtf" contenteditable="true">{val_mtf}</div></td></tr></table><div class="aim-footer">AIM Module</div></div>'''
            return register_ph(html)

        text = re.sub(r'\[\[include :scp-wiki-cn:component:advanced-information-methodology.*?\]\]', aim_replacer, text, flags=re.DOTALL)

        # --- 3. Image Block (Basic & Adv) ---
        def img_replacer(match):
            block = match.group(0)
            def get_arg(name): 
                m = re.search(fr'(?:\||\s){name}=([^\|\n\]]+)', block, re.IGNORECASE)
                return m.group(1).strip() if m else ""
            name = get_arg('name')
            caption = get_arg('caption')
            width = get_arg('width')
            height = get_arg('height')
            align = get_arg('align') or 'right'
            is_adv = bool(width or height)
            c_type = "image-block-adv" if is_adv else "image-block"
            dim_html = ""
            if is_adv:
                 dim_html = f'''<div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div><b>源:</b> <span data-field="name" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:50px; display:inline-block; border-bottom:1px dashed #ccc;">{name}</span></div><div><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{width}</span> <b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{height}</span></div></div>'''
            else:
                 dim_html = f'''<div style="background:#fff; padding:5px; text-align:center; border-bottom:1px solid #eee; font-size:0.9em;"><b>源:</b> <span data-field="name" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:50px; display:inline-block; border-bottom:1px dashed #ccc;">{name}</span></div>'''
            # Removed clear:both div
            html = f'''<div class="scp-component image-block-box" data-type="{c_type}" data-align="{align}" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div>{dim_html}</div><div class="image-block-content"><img src="{name}" class="img-preview" style="max-width:100%; display:block; margin:0 auto 5px auto;"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;display:none;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">{caption}</span></div></div>'''
            return register_ph(html)

        text = re.sub(r'\[\[include component:image-block.*?\]\]', img_replacer, text, flags=re.DOTALL)

        # --- 4. Tabview ---
        def tabview_replacer(match):
            content = match.group(1)
            tabs = re.findall(r'\[\[tab ([^\]]+)\]\](.*?)\[\[/tab\]\]', content, flags=re.DOTALL)
            header_html = ""
            body_html = ""
            for i, (title, body) in enumerate(tabs):
                active = " active" if i == 0 else ""
                header_html += f'<span class="tab-btn{active}" onclick="selectTab(this)" contenteditable="true">{title.strip()}</span>'
                # Recursive call is kept AS IS, protecting its result inside the body
                parsed_body = self.parse_wikidot_to_editor_html(body)
                body_html += f'<div class="tab-item{active}" contenteditable="true">{parsed_body}</div>'
            html = f'''<div class="scp-component tabview-box" data-type="tabview" contenteditable="false"><div class="tab-header">{header_html}<span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents">{body_html}</div></div>'''
            return register_ph(html)
            
        text = re.sub(r'\[\[tabview\]\](.*?)\[\[/tabview\]\]', tabview_replacer, text, flags=re.DOTALL)

        # --- 4.5 Login/Logout (fakeprot) Pre-processor ---
        # Must run BEFORE collapsible_replacer so the [[collapsible show="登入" hide="登出"]]
        # adjacent to [[div class="fakeprot"]] is consumed together as one widget and
        # not split into a separate collapsible-box.
        _FAKEPROT_EARLY_SIG = '.fakeprot .mailform-box .buttons'
        if _FAKEPROT_EARLY_SIG in text:
            def process_fakeprot_source(txt):
                result = []
                cursor = 0
                # Pattern to find [[div class="fakeprot"]] (and single-quote variant)
                pat_div_start = re.compile(
                    r'\[\[div\s+class=["\']fakeprot["\']\]\]', re.IGNORECASE
                )
                pat_div_close = re.compile(r'\[\[/div\]\]', re.IGNORECASE)
                pat_coll = re.compile(
                    r'\s*\[\[collapsible\s+show="([^"]*)"\s+hide="([^"]*)"\]\](.*?)\[\[/collapsible\]\]',
                    re.DOTALL | re.IGNORECASE
                )

                for m_start in pat_div_start.finditer(txt):
                    div_start = m_start.start()
                    if div_start < cursor:
                        continue  # already consumed

                    # Balance-scan for matching [[/div]]
                    depth = 1
                    i = m_start.end()
                    div_end = None
                    while i < len(txt) and depth > 0:
                        next_open = re.search(r'\[\[div', txt[i:], re.IGNORECASE)
                        next_close = pat_div_close.search(txt[i:])
                        if not next_close:
                            break
                        pos_close = i + next_close.start()
                        pos_open = i + next_open.start() if next_open else -1
                        if next_open and pos_open < pos_close:
                            depth += 1
                            i = pos_open + 5
                        else:
                            depth -= 1
                            i = pos_close + 8  # len('[[/div]]')
                            if depth == 0:
                                div_end = i  # exclusive end (after [[/div]])

                    if div_end is None:
                        continue  # unbalanced, skip

                    inner_content = txt[m_start.end(): div_end - 8]  # content inside div

                    # Check for adjacent [[collapsible show="登入" hide="登出"]]
                    coll_m = pat_coll.match(txt, div_end)
                    if coll_m:
                        coll_content_raw = coll_m.group(3)
                        block_end = coll_m.end()
                    else:
                        coll_content_raw = '文字'
                        block_end = div_end

                    # Extract ID default value
                    id_dm = re.search(r'\*\s*default:\s*<([^>]+)>', inner_content)
                    id_val = id_dm.group(1).strip() if id_dm else '你的ID'

                    # Parse collapsible content
                    parsed_coll = self.parse_wikidot_to_editor_html(coll_content_raw.strip())

                    # Build login-logout-box
                    ll_html = (
                        '<div class="scp-component login-logout-box" data-type="login-logout"'
                        ' contenteditable="false"'
                        ' style="border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;">'
                        '<table class="login-form-table" contenteditable="false"'
                        ' style="margin:0.5em auto; border-collapse:collapse;">'
                        '<tr>'
                        '<td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">ID</td>'
                        '<td>'
                        f'<span class="login-id-value" contenteditable="true"'
                        f' style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;">'
                        f'{id_val}</span>'
                        '</td>'
                        '</tr>'
                        '<tr>'
                        '<td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">\u5bc6\u7801</td>'
                        '<td>'
                        '<span contenteditable="false"'
                        ' style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px;'
                        ' font-family:sans-serif; color:#555; letter-spacing:2px;">'
                        '\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb\u30fb</span>'
                        '</td>'
                        '</tr>'
                        '<tr>'
                        '<td contenteditable="false"></td>'
                        '<td style="text-align:center;" contenteditable="false">'
                        '<button contenteditable="false"'
                        ' style="padding:2px 18px; border:1px solid #aaa; background:#f4f4f4; cursor:pointer; font-family:sans-serif;">'
                        '\u767b\u5165</button>'
                        '</td>'
                        '</tr>'
                        '</table>'
                        '<hr contenteditable="false" style="border:none; border-top:1px solid #ccc; margin:6px 0;">'
                        '<div contenteditable="false"'
                        ' style="font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;">'
                        '[\u767b\u5165]\u2194[\u767b\u51fa] \u6298\u53e0\u5185\u5bb9</div>'
                        '<div class="login-collapsible-content" contenteditable="true"'
                        ' style="min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;">'
                        f'{parsed_coll}'
                        '</div>'
                        '</div>'
                    )
                    result.append(txt[cursor:div_start])
                    result.append(register_ph(ll_html))
                    cursor = block_end

                result.append(txt[cursor:])
                return ''.join(result)

            text = process_fakeprot_source(text)

        # --- 5. Collapsible ---
        def collapsible_replacer(match):
            show_t = match.group(1) or "+ Open"
            hide_t = match.group(2) or "- Close"
            content = match.group(3)
            parsed_inner = self.parse_wikidot_to_editor_html(content)
            html = f'''<div class="scp-component collapsible-box open" data-type="collapsible" contenteditable="false"><div class="collapsible-header"><span><span class="title-label">显示标题:</span> <span class="title-input" data-field="show" contenteditable="true">{show_t}</span></span><span><span class="title-label">隐藏标题:</span> <span class="title-input" data-field="hide" contenteditable="true">{hide_t}</span></span></div><div class="collapsible-content-area" contenteditable="true">{parsed_inner}</div></div>'''
            return register_ph(html)

        text = re.sub(r'\[\[collapsible show="([^"]*)" hide="([^"]*)"\]\](.*?)\[\[/collapsible\]\]', collapsible_replacer, text, flags=re.DOTALL)

        # --- 5.5 DIV Module (Updated for Shortcuts) ---
        # --- 5.5.1 Helper for Nested Divs ---
        def process_nested_divs(text):
            # Iteratively find [[div ...]] ... [[/div]] blocks, respecting nesting.
            # We process from Start to End.
            # If we find a block, we replace it with a placeholder and recursively process the inside?
            # actually, div_replacer calls parse_wikidot_to_editor_html(content), which handles recursion.
            # so we just need to identify the *outermost* blocks correctly.
            
            output = []
            cursor = 0
            while True:
                # Find start of [[div
                start_idx = text.find('[[div', cursor)
                if start_idx == -1:
                    output.append(text[cursor:])
                    break
                
                # Append text before the div
                output.append(text[cursor:start_idx])
                
                # Verify it's a valid tag start (not just text) and extract parameters
                # [[div params]]
                # Find the closing ]] of the opening tag
                content_start_idx = text.find(']]', start_idx)
                if content_start_idx == -1:
                    # Malformed, no closing brackets for tag
                    output.append(text[start_idx:])
                    break
                
                params = text[start_idx+5 : content_start_idx].strip()
                content_start_idx += 2 # Skip ']]'
                
                # Now scan for balancing [[/div]]
                nesting = 1
                current = content_start_idx
                found_end = False
                
                while True:
                    next_open = text.find('[[div', current)
                    next_close = text.find('[[/div]]', current)
                    
                    if next_close == -1:
                        # No closing tag found at all
                        break
                        
                    if next_open != -1 and next_open < next_close:
                        # Found a nested opening tag
                        nesting += 1
                        current = next_open + 5
                    else:
                        # Found a closing tag
                        nesting -= 1
                        current = next_close + 8 # length of [[/div]]
                        
                        if nesting == 0:
                            found_end = True
                            break
                            
                if found_end:
                    # Extract full content
                    content = text[content_start_idx : next_close]
                    
                    # Call replacements
                    # Note: div_replacer needs to be adapted to accept (params, content)
                    # We wrap it here.
                    replaced_html = div_replacer(None, params, content)
                    output.append(replaced_html)
                    
                    # Update cursor to after the closing [[/div]]
                    cursor = next_close + 8
                else:
                    # Unbalanced text, just treat as text
                    output.append(text[start_idx:])
                    break
                    
            return "".join(output)

        # --- 5.5 DIV Module (Updated for Shortcuts) ---
        # Detect page-note CSS signature early so div_replacer can use it as a closure.
        _PAGE_CSS_SIG = 'linear-gradient(to top ,rgb(202, 219, 228) 0%, rgb(231, 233, 220) 8%)'
        _has_page_css = [_PAGE_CSS_SIG in text]  # mutable list so closure can read it
        _PAGE_NOTE_STYLE = (
            'display:block; overflow:hidden; '
            "font-family:'Monotype Corsiva','Bradley Hand ITC',sans-serif; "
            'background-attachment:scroll; '
            'background-image:linear-gradient(to top,rgb(202,219,228) 0%,rgb(231,233,220) 8%); '
            'background-position:0px 8px; background-repeat:repeat; background-size:100% 20px; '
            'border:1px solid #CCC; border-radius:10px; padding:10px; margin-bottom:10px; '
            'box-shadow:0px 1px 3px rgba(0,0,0,0.2); position:relative; clear:both;'
        )

        # Detect login/logout (fakeprot) CSS signature early.
        _FAKEPROT_CSS_SIG = '.fakeprot .mailform-box .buttons'
        _has_fakeprot_css = [_FAKEPROT_CSS_SIG in text]  # mutable list so closure can read it

        def div_replacer(match=None, params_arg=None, content_arg=None):
            if match:
                params = match.group(1).strip()
                content = match.group(2)
            else:
                params = params_arg
                content = content_arg

            # --- Terminal #001 check FIRST (before computing parsed_inner) ---
            # Must be before parsed_inner to prevent premature [[=]]/[[size]] processing
            if 'class="terminal"' in params or "class='terminal'" in params:
                 # Helper: extract balanced [[div class="X"]]...[[/div]] content
                 def extract_div_content(src, cls_marker):
                     pat1 = f'[[div class="{cls_marker}"]]'
                     pat2 = f"[[div class='{cls_marker}']]"
                     start = src.find(pat1)
                     quote_len = len(pat1)
                     if start == -1:
                         start = src.find(pat2)
                         quote_len = len(pat2)
                     if start == -1:
                         return None
                     body_start = start + quote_len
                     depth = 1
                     i = body_start
                     while i < len(src) and depth > 0:
                         next_open = src.find('[[div', i)
                         next_close = src.find('[[/div]]', i)
                         if next_close == -1:
                             break
                         if next_open != -1 and next_open < next_close:
                             depth += 1
                             i = next_open + 5
                         else:
                             depth -= 1
                             if depth == 0:
                                 return src[body_start:next_close]
                             i = next_close + 8
                     return None

                 text_content = extract_div_content(content, 'text')

                 if text_content is not None:
                     # Convert bare HR lines (------) to @------@ for proper dash rendering
                     def fix_hr_lines(txt):
                         lines = txt.split('\n')
                         out = []
                         for ln in lines:
                             if re.match(r'^-{4,}\s*$', ln):
                                 count = len(ln.rstrip())
                                 out.append('@' + '-' * count + '@')
                             else:
                                 out.append(ln)
                         return '\n'.join(out)
                     text_content = fix_hr_lines(text_content.strip())
                     parsed_text = self.parse_wikidot_to_editor_html(text_content)

                     html = f'''<div class="scp-component div-box terminal" data-type="div-block" contenteditable="false">
                     <div class="div-header" onclick="toggleDiv(this)" style="cursor:pointer;" title="点击折叠/展开">DIV: class="terminal"</div>
                     <div class="div-content" contenteditable="true">
                        <div class="scp-component div-box scanline" data-type="div-block" contenteditable="false">
                            <div class="div-header" onclick="toggleDiv(this)" style="cursor:pointer;" title="点击折叠/展开">DIV: class="scanline"</div>
                            <div class="div-content" contenteditable="true"></div>
                        </div>
                        <div class="scp-component div-box text" data-type="div-block" contenteditable="false">
                            <div class="div-header" onclick="toggleDiv(this)" style="cursor:pointer;" title="点击折叠/展开">DIV: class="text"</div>
                            <div class="div-content" contenteditable="true">{parsed_text}</div>
                        </div>
                     </div>
                     </div>'''
                     return register_ph(html)

            # For all other divs: compute parsed_inner lazily here
            parsed_inner = self.parse_wikidot_to_editor_html(content)
            if "border: 1px solid #FFC107" in params or "border: 1px solid rgb(255, 193, 7)" in params:
                 # Reconstruct RAISA Box
                 html = f'''<div class="scp-component raisa-box" data-type="raisa-notice" contenteditable="false"><div class="raisa-header" contenteditable="false">NOTICE FROM THE RECORDS AND INFORMATION SECURITY ADMINISTRATION</div><div class="raisa-content" contenteditable="true">{parsed_inner}</div><div class="raisa-footer" contenteditable="false"></div></div>'''
                 return register_ph(html)

            # 2. Check for Class Warning
            if "scp_trans.png" in params and ("border: solid 2px black" in params or "border: 2px solid black" in params):
                 # Reconstruct Class Warning Box
                 html = f'''<div class="scp-component class-warning-box" data-type="class-warning" contenteditable="false"><div class="class-warning-content" contenteditable="true"><div class="class-warning-inner">{parsed_inner}</div></div></div>'''
                 return register_ph(html)

            # 3. Check for O5 Command
            if "kaktuskontainer" in params and "width: 600px" in params:
                 # Reconstruct O5 Command Box
                 html = f'''<div class="scp-component o5-box" data-type="o5-command" contenteditable="false"><div class="o5-content" contenteditable="true">{parsed_inner}</div></div>'''
                 return register_ph(html)

            # --- Page Note (class="page" when matching CSS module is in the document) ---
            if _has_page_css[0] and ('class="page"' in params or "class='page'" in params):
                html = (f'<div class="scp-component page-note-box" data-type="page-note" '
                        f'contenteditable="false" style="{_PAGE_NOTE_STYLE}">'
                        f'<div class="page-note-label" contenteditable="false" '
                        f'style="font-size:10px;color:#aaa;text-align:right;margin-bottom:2px;">便签纸</div>'
                        f'<div class="page-note-content" contenteditable="true" '
                        f'style="font-family:\'Monotype Corsiva\',\'Bradley Hand ITC\',sans-serif;line-height:20px;">'
                        f'{parsed_inner}</div></div>')
                return register_ph(html)

            # Standard DIV (with Collapse Toggle)
            html = f'''<div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true" onclick="toggleDiv(this)" style="cursor:pointer;" title="点击折叠/展开">DIV: {params}</div><div class="div-content" contenteditable="true">{parsed_inner}</div></div>'''
            return register_ph(html)

        # REPLACE REGEX with Custom Parser
        # --- 5.5a. Pre-detect RAISA / CLASS WARNING / O5 components ---
        # These are identified by unique strings in their inline style attributes.
        # We handle them HERE (before process_nested_divs) so they get the SAME
        # styled HTML as sidebar insertion, avoiding any content-rendering issues.
        def extract_top_div(txt, start_pos):
            """Extract full [[div ...]]...[[/div]] block starting at start_pos.
            Returns (params_str, inner_content, end_pos_exclusive) or None."""
            # Find closing ]] of opening tag
            tag_end = txt.find(']]', start_pos)
            if tag_end == -1: return None
            params_str = txt[start_pos + 5 : tag_end].strip()  # after [[div
            # Balanced scan for [[/div]]
            depth = 1
            i = tag_end + 2
            while i < len(txt) and depth > 0:
                next_open = txt.find('[[div', i)
                next_close = txt.find('[[/div]]', i)
                if next_close == -1: break
                if next_open != -1 and next_open < next_close:
                    depth += 1; i = next_open + 5
                else:
                    depth -= 1
                    if depth == 0:
                        inner = txt[tag_end + 2 : next_close]
                        return (params_str, inner, next_close + 8)
                    i = next_close + 8
            return None

        def pre_detect_components(txt):
            """Scan for RAISA / CLASS WARNING / O5 divs and replace with styled HTML."""
            result = []
            cursor = 0
            while True:
                pos = txt.find('[[div', cursor)
                if pos == -1:
                    result.append(txt[cursor:])
                    break
                info = extract_top_div(txt, pos)
                if info is None:
                    result.append(txt[cursor:])
                    break
                params_str, inner_content, end_pos = info
                matched = False

                # --- RAISA Notice ---
                if 'FFC107' in params_str or 'rgb(255, 193, 7)' in params_str:
                    result.append(txt[cursor:pos])
                    parsed_inner = self.parse_wikidot_to_editor_html(inner_content)
                    raisa_style = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5; position: relative; clear: both;"
                    html = (f'<div class="scp-component raisa-box" data-type="raisa-notice" contenteditable="false" style="{raisa_style}">'
                            f'<div class="raisa-header" contenteditable="false" style="text-align:center; font-weight:bold; border-bottom:1px solid #FFC107; margin-bottom:8px; padding-bottom:4px;">NOTICE FROM THE RECORDS AND INFORMATION SECURITY ADMINISTRATION</div>'
                            f'<div class="raisa-content" contenteditable="true" style="text-align:center;">{parsed_inner}</div>'
                            f'<div class="raisa-footer" contenteditable="false"></div></div>')
                    result.append(register_ph(html))
                    cursor = end_pos; matched = True

                # --- O5 Command (kaktuskontainer + 600px) ---
                elif 'kaktuskontainer' in params_str and '600px' in params_str:
                    result.append(txt[cursor:pos])
                    parsed_inner = self.parse_wikidot_to_editor_html(inner_content)
                    o5_style = "background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px; position: relative; clear: both;"
                    html = (f'<div class="scp-component o5-box" data-type="o5-command" contenteditable="false" style="{o5_style}">'
                            f'<div class="o5-content" contenteditable="true">{parsed_inner}</div></div>')
                    result.append(register_ph(html))
                    cursor = end_pos; matched = True

                # --- CLASS WARNING (the-great-hippo bg + solid 2px black border) ---
                elif 'the-great-hippo' in params_str and 'solid 2px black' in params_str:
                    result.append(txt[cursor:pos])
                    parsed_inner = self.parse_wikidot_to_editor_html(inner_content)
                    cw_style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) center no-repeat; border: solid 2px #000; padding: 1px 15px; box-shadow: 0 1px 3px rgba(0,0,0,.2); margin: 10px auto; width: fit-content; text-align: center; position: relative; clear: both;"
                    html = (f'<div class="scp-component class-warning-box" data-type="class-warning" contenteditable="false" style="{cw_style}">'
                            f'<div class="class-warning-content" contenteditable="true">'
                            f'<div class="class-warning-inner" style="text-align:center;">{parsed_inner}</div>'
                            f'</div></div>')
                    result.append(register_ph(html))
                    cursor = end_pos; matched = True

                if not matched:
                    result.append(txt[cursor:pos + 5])
                    cursor = pos + 5

            return ''.join(result)


        text = pre_detect_components(text)
        text = process_nested_divs(text)

        # --- 5.6 CSS Module ---
        def css_replacer(match):
            content = match.group(1).strip()

            # --- Page Note CSS: suppress silently (already handled by pre_detect_components) ---
            PAGE_CSS_SIG = 'linear-gradient(to top ,rgb(202, 219, 228) 0%, rgb(231, 233, 220) 8%)'
            if PAGE_CSS_SIG in content:
                return ''  # consumed by page-note-box; don't render a css-box

            # --- Login/Logout (fakeprot) CSS: suppress silently ---
            if '.fakeprot .mailform-box .buttons' in content:
                return ''  # consumed by login-logout-box; don't render a css-box

            # Check for Terminal Style Signature
            is_terminal = ".danke" in content and ".agent" in content
            
            if is_terminal:
                # Collapsible CSS Module for Terminal Style
                html = f'''<div class="scp-component css-box" data-type="css-module" contenteditable="false">
                <details>
                    <summary class="css-header" style="cursor:pointer; user-select:none;">CSS Module (Terminal Style) - 点击折叠/展开</summary>
                    <div class="css-content" contenteditable="true">{content}</div>
                </details>
                <div class="css-hint">被css影响的代码紧跟css模块下面</div></div>'''
            else:
                # Standard CSS Module (Now Collapsible)
                html = f'''<div class="scp-component css-box" data-type="css-module" contenteditable="false"><div class="css-header" onclick="toggleCss(this)" style="cursor:pointer;" title="点击折叠/展开">CSS Module (Valid CSS Only) (点击折叠)</div><div class="css-content" contenteditable="true">{content}</div><div class="css-hint">被css影响的代码紧跟css模块下面</div></div>'''
            
            return register_ph(html)

        text = re.sub(r'\[\[module CSS\]\](.*?)\[\[/module\]\]', css_replacer, text, flags=re.DOTALL|re.IGNORECASE)

        # --- 6. Users ---
        def user_replacer(match):
            html = f'<span class="scp-component user-tag" data-type="user" contenteditable="false"><div class="user-icon"></div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{match.group(1)}</span></span>'
            return register_ph(html)
        text = re.sub(r'\[\[user ([^\]]+)\]\]', user_replacer, text)
        
        def user_adv_replacer(match):
            html = f'<span class="scp-component user-tag" data-type="user-adv" contenteditable="false"><div class="user-icon" style="background:gold; text-align:center; line-height:12px; font-size:10px; color:#fff;">★</div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{match.group(1)}</span></span>'
            return register_ph(html)
        text = re.sub(r'\[\[\*user ([^\]]+)\]\]', user_adv_replacer, text)

        # --- 7. TOC ---
        def toc_replacer(match):
             html = '<div class="scp-component" data-type="toc" contenteditable="false" style="border: 1px dashed #999; padding: 5px; background: #f0f0f0;"><b>目录 (TOC)</b><br>[[toc]]</div>'
             return register_ph(html)
        text = re.sub(r'\[\[toc\]\]', toc_replacer, text)

        # --- 8. Footnotes ---
        def fn_replacer(match):
            content = match.group(1)
            # Add title attribute for tooltip
            html = f'<span class="scp-component scp-footnote" data-type="footnote" data-content="{content}" title="{content}" contenteditable="false">#</span>'
            return register_ph(html)
        text = re.sub(r'\[\[footnote\]\](.*?)\[\[/footnote\]\]', fn_replacer, text, flags=re.DOTALL)
        
        # --- 8.5 Font Size, Alignment & Color (AFTER module extraction) ---
        text = re.sub(r'\[\[\s*size\s+([^\]]+)\]\](.*?)\[\[\s*/size\s*\]\]', r'<span style="font-size:\1">\2</span>', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'\[\[\s*<\s*\]\](.*?)\[\[\s*/<\s*\]\]', r'<div style="text-align: left;">\1</div>', text, flags=re.DOTALL)
        text = re.sub(r'\[\[\s*>\s*\]\](.*?)\[\[\s*/>\s*\]\]', r'<div style="text-align: right;">\1</div>', text, flags=re.DOTALL)
        text = re.sub(r'\[\[\s*==\s*\]\](.*?)\[\[\s*/==\s*\]\]', r'<div style="text-align: justify;">\1</div>', text, flags=re.DOTALL)
        text = re.sub(r'\[\[\s*=\s*\]\](.*?)\[\[\s*/=\s*\]\]', r'<div style="text-align: center;">\1</div>', text, flags=re.DOTALL)
        # ## color | text ## — Wikidot inline color markup
        # group 1: color value (no |, #, newline)
        # group 2: content — allow single # (e.g. #/XXXX) but NOT ## (closing delimiter)
        text = re.sub(r'##([^|#\n]+)\|((?:[^#]|#(?!#))+)##',
                      lambda m: f'<span style="color: {m.group(1).strip()}">{m.group(2)}</span>',
                      text)

        # --- 9. Standard Tables & Blockquotes (Merged) ---
        lines = text.split('\n')
        final_lines = []
        buffer_table = []
        buffer_quote = []
        
        def flush_table():
            if not buffer_table: return
            # Construct table HTML
            t_html = '<table border="1" class="wikidot-table">'
            for row in buffer_table:
                cells = [c for c in row.split('||') if c]
                t_html += "<tr>"
                for c in cells:
                    tag = "td"
                    c_text = c
                    if c.startswith('~'):
                        tag = "th"
                        c_text = c[1:]
                    t_html += f'<{tag} contenteditable="true">{c_text.strip()}</{tag}>'
                t_html += "</tr>"
            t_html += "</table>"
            final_lines.append(register_ph(t_html))
            buffer_table.clear()

        def flush_quote():
            if not buffer_quote: return
            # Join with BR for visual line break
            content = "<br>".join(buffer_quote)
            final_lines.append(f'<blockquote>{content}</blockquote>')
            buffer_quote.clear()

        for line in lines:
            line = line.rstrip('\r\n') # trim newline
            # Check for Table
            if line.startswith('||') and line.endswith('||') and '_WIKIDOT_PH_' not in line:
                flush_quote()
                buffer_table.append(line)
            # Check for Blockquote (permissive: starting with >)
            elif line.startswith('>'):
                flush_table()
                # Remove '>' and optionally one following space
                q_line = line[1:]
                if q_line.startswith(' '): q_line = q_line[1:]
                buffer_quote.append(q_line)
            else:
                flush_table()
                flush_quote()
                final_lines.append(line)
        flush_table()
        flush_quote()
        text = "\n".join(final_lines)

        # --- 9.5 Custom Dash Render (Prevent HR) ---
        # User requested @------@ to be rendered as dashes, not HR.
        # We replace @---@ with dashes wrapped in a span to protect from HR regex.
        # HR regex is ^-{4,}\s*$
        def dash_protector(m):
            count = len(m.group(1))
            # Use HTML entities so strikethrough regex (--(x)--) and HR (^----$) don't match
            # Visual: shows just the dashes (no @ signs) — @ is only the INPUT protection syntax
            visual = '&#45;' * count
            return f'<span class="custom-dash" data-count="{count}">{visual}</span>'
        text = re.sub(r'@(-{3,})@', dash_protector, text)

        # --- 10. Headers & Basic Formatting ---
        text = re.sub(r'^(\+{1,6})\s+(.*)$', lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>', text, flags=re.MULTILINE)
        
        def hr_replacer(m): return register_ph('<div class="scp-hr scp-component" data-type="hr" contenteditable="false"></div>')
        # Fix: Allow trailing spaces for HR
        text = re.sub(r'^-{4,}\s*$', hr_replacer, text, flags=re.MULTILINE)
        
        # Blockquotes handled in loop above
        pass
        
        # Bold/Italic - Now Safe because components are hidden
        # But wait, URLs inside components are hidden in placeholders, so they are safe!
        # What about URLs in plain text? "http://example.com"
        # We might still want to auto-link them? Editor usually auto-links on type.
        # But if we inject HTML, we should link them.
        # BUT the priority is solving "https://..." corrupted by Italics "//"
        # Since components are hidden, their https:// are safe.
        # Plain text URLs: "Check https://site.com" -> "//" might match italic?
        # Yes. "https://site.com" contains "//".
        # If we have "check //italic//", regex matches //...//
        # If we have "https://site.com", does it match?
        # A simple `//(.*?)//` matches `//site.com` if not careful.
        # Improvement: Italic usually requires space or bound.
        # Wikidot syntax `//text//`.
        # Standard fix: `(?<!:)//(.*?)//` ?
        
        # Bold (** must come before single * italic)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # Single-star italic (*text*) — Wikidot's alternative italic syntax
        # Must NOT match ** (already consumed) or URLs
        text = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        
        # Italic - Fix for URL interference: lookbehind not colons?
        text = re.sub(r'(?<!:)//(.*?)//', r'<i>\1</i>', text)
        
        # Underline, Strikethrough, Monospace
        text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)
        text = re.sub(r'--(.*?)--', r'<s>\1</s>', text)
        text = re.sub(r'\{\{(.*?)\}\}', r'<span style="font-family: monospace">\1</span>', text)
        
        # Color
        # Color
        text = re.sub(r'##([^\|]+)\|([^#]+)##', r'<font color="\1">\2</font>', text)
        
        # Size and Alignment moved to TOP of function
        pass

        # Links
        # 1. Standard [[[url | text]]]
        text = re.sub(r'\[\[\[([^\|\]]+)\|\s*(.*?)\]\]\]', r'<a href="\1">\2</a>', text)
        # 2. New [url text] - Broaden to support internal links, excluding [[...]]
        def link_replacer_single(match):
            url = match.group(1)
            text_content = match.group(2)
            
            # 1. Enforce Protocol: Must start with http:// or https://
            if not (url.startswith('http://') or url.startswith('https://')):
                 return match.group(0)
            
            # 2. Keywords to exclude (Redaction)
            exclude_keywords = ["已编辑", "数据删除", "数据已删除", "咒骂声", "尖叫声","DATA EXPUNGED", "REDACTED", "DATA LOST", "数据丢失"]
            
            upper_text = text_content.upper()
            for kw in exclude_keywords:
                if kw in upper_text:
                    return match.group(0) # Return original text
            
            return f'<a href="{url}">{text_content}</a>'

        text = re.sub(r'(?<!\[)\[([^\[\s]\S*)\s+([^\]]+)\]', link_replacer_single, text)
        
        # Placeholder Restoration
        # Must restore explicitly
        # Note: Recursive placeholders might exist? 
        # Our `register_ph` generates unique tokens so order of restoration just needs to process string.
        # But since we call `parse_wikidot_to_editor_html` recursively in logic, the INNER logic returns just PH tokens as text for outer logic?
        # WAIT. `tabview_replacer` calls `self.parse_wikidot_to_editor_html(body)`.
        # That recursive call will return a string with PH tokens in it (from its own scope), OR restored HTML?
        # Function returns RESTORED HTML.
        # So `parsed_body` contains HTML tags.
        # Outer parse receives HTML string.
        # Outer parse wraps it in `tab-contents`.
        # Outer parse registers `<div class="tabview">...<div class="acs">...</div>...</div>` as `_PH_0_` (Outer's 0).
        # Finally Outer parse restores `text`.
        # It works.
        
        # Newline Handling (Fix for "Editor renders un-wrapped")
        # Convert newlines to <br> to ensure visual line breaks in HTML
        # Must be done AFTER regex line-processing (like Headers) but BEFORE placeholder restoration
        # (Placeholders are safe timestamps, but we don't want to break them? No, tokens are _PH_X_ no spaces)
        # Convert newlines to <br> to ensure visual line breaks in HTML
        # REMOVED: Return symbol text.replace('\n', '<span class="cr-symbol" ...>↵</span><br>')
        text = text.replace('\n', '<br>')

        for k, v in placeholders.items():
            text = text.replace(k, v)
        
        return text




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SCPEditor()
    window.show()
    sys.exit(app.exec())