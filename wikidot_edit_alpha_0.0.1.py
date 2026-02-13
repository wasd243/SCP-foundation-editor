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
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QPoint
from PyQt6.QtGui import QAction, QIcon

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


class SCPEditor(QMainWindow):
    """
    SCP Foundation Wiki 文档创作助手 - 功能增强版
    逻辑更新：
    - 新增：标题等级选择 (H1-H6)，对应维基语法的 + 到 ++++++。
    - 新增：URL 链接插入功能，支持 [[[url | text]]] 和 [[[ *url | text ]]] (新窗口) 语法。
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
        """)

        # --- 工具栏 ---
        toolbar = QToolBar("格式工具栏")
        toolbar.setStyleSheet("QToolBar { icon-size: 24px; }")
        main_layout.addWidget(toolbar)

        # 1. 标题选择器 (新增)
        self.heading_selector = QComboBox()
        self.heading_selector.addItems([
            "正文 (Paragraph)",
            "1级标题 (+)",
            "2级标题 (++)",
            "3级标题 (+++)",
            "4级标题 (++++)",
            "5级标题 (+++++)",
            "6级标题 (++++++)"
        ])
        self.heading_selector.setMinimumWidth(150)
        self.heading_selector.currentIndexChanged.connect(self.set_heading)
        toolbar.addWidget(self.heading_selector)

        toolbar.addSeparator()

        actions = [
            ("加粗", "bold"),
            ("斜体", "italic"),
            ("下划线", "underline"),
            ("删除线", "strikeThrough")
        ]

        for text, command in actions:
            action = QAction(text, self)
            action.triggered.connect(lambda checked, cmd=command: self.exec_format(cmd))
            toolbar.addAction(action)

        sup_action = QAction("上标", self)
        sup_action.triggered.connect(lambda: self.exec_format("superscript"))
        toolbar.addAction(sup_action)

        sub_action = QAction("下标", self)
        sub_action.triggered.connect(lambda: self.exec_format("subscript"))
        toolbar.addAction(sub_action)

        mono_action = QAction("等宽", self)
        mono_action.triggered.connect(lambda: self.browser.page().runJavaScript("toggleMonospace();"))
        toolbar.addAction(mono_action)

        toolbar.addSeparator()

        color_action = QAction("文字颜色", self)
        color_action.triggered.connect(self.choose_color)
        toolbar.addAction(color_action)

        # 2. 插入链接 (新增)
        link_action = QAction("插入链接", self)
        link_action.setToolTip("插入 URL 链接")
        link_action.triggered.connect(self.open_link_dialog)
        toolbar.addAction(link_action)

        toolbar.addSeparator()

        ul_action = QAction("无序列表", self)
        ul_action.triggered.connect(lambda: self.exec_format("insertUnorderedList"))
        toolbar.addAction(ul_action)

        ol_action = QAction("有序列表", self)
        ol_action.triggered.connect(lambda: self.exec_format("insertOrderedList"))
        toolbar.addAction(ol_action)

        quote_action = QAction("引用块", self)
        quote_action.triggered.connect(lambda: self.exec_format("formatBlock", "blockquote"))
        toolbar.addAction(quote_action)

        toolbar.addSeparator()

        hr_action = QAction("分割线", self)
        hr_action.triggered.connect(self.insert_hr)
        toolbar.addAction(hr_action)

        table_action = QAction("表格", self)
        table_action.triggered.connect(self.insert_table)
        toolbar.addAction(table_action)

        toc_action = QAction("目录", self)
        toc_action.triggered.connect(self.insert_toc)
        toolbar.addAction(toc_action)

        left_align_action = QAction("靠左", self)
        left_align_action.triggered.connect(lambda: self.exec_format("justifyLeft"))
        toolbar.addAction(left_align_action)

        right_align_action = QAction("靠右", self)
        right_align_action.triggered.connect(lambda: self.exec_format("justifyRight"))
        toolbar.addAction(right_align_action)

        toggle_dock_action = QAction("显示/隐藏页面属性", self)
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
            "高级分级组件 (ACS/CN)",
            "版式",
            "AIM 高级信息方法论",
            "图片块 (Image Block)",
            "高级图片块 (Advanced Image)",
            "选项卡 (Tab View)",
            "用户信息 (User)",
            "高级用户信息 (Advanced User)",
            "折叠块 (Collapsible)",
            "授权引用 (最新格式)",
            "脚注"
        ])
        self.comp_selector.currentIndexChanged.connect(self.toggle_config_panels)
        comp_layout.addWidget(self.comp_selector)

        # --- 版式配置 ---
        self.basalt_group = QGroupBox("版式与全局设置")
        self.basalt_group.setVisible(False)
        basalt_vbox = QVBoxLayout()

        self.check_better_footnotes = QCheckBox("启用 Better Footnotes (更好的脚注)")
        self.check_better_footnotes.setStyleSheet("color: red; font-weight: bold; font-size: 13px; padding: 5px;")
        self.check_better_footnotes.setToolTip("开启后将自动转换脚注格式并移除 footnoteblock")
        basalt_vbox.addWidget(self.check_better_footnotes)

        self.check_enable_basalt = QCheckBox("启用玄武岩主题")
        self.check_enable_basalt.toggled.connect(self.on_basalt_toggled)
        basalt_vbox.addWidget(self.check_enable_basalt)

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

        basalt_vbox.addWidget(self.basalt_sub_options_frame)
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

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入维基页面 URL...")
        source_layout.addWidget(self.url_input)

        fetch_btn = QPushButton("抓取在线源码")
        fetch_btn.clicked.connect(self.fetch_source)
        source_layout.addWidget(fetch_btn)

        self.source_display = QTextEdit()
        self.source_display.setPlaceholderText("生成的维基代码将在此显示...")
        source_layout.addWidget(self.source_display)

        left_panel.addTab(comp_tab, "编辑器")
        left_panel.addTab(source_tab, "代码视窗")

        self.browser = QWebEngineView()
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

        self.right_dock_layout.addWidget(self.lbl_theme_status)
        self.right_dock_layout.addWidget(self.lbl_bf_status)
        self.right_dock_layout.addStretch()

        self.right_dock.setWidget(self.right_dock_content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

    def init_editor_html(self):
        content = r"""
        <html>
        <head>
            <style>
                /* 修改行间距为 1.4 */
                body { font-family: 'Verdana', sans-serif; padding: 40px; line-height: 1.4; background: #fff; position: relative; }
                #editor-root { min-height: 400px; outline: none; padding-bottom: 50px; }

                /* 链接样式 */
                a { color: #b01; text-decoration: none; cursor: pointer; }
                a:hover { text-decoration: underline; }

                .rate-module-box {
                    position: absolute; top: 20px; right: 40px; background: #eee;
                    border: 1px solid #ccc; padding: 5px 10px; font-size: 12px;
                    color: #666; border-radius: 3px; user-select: none;
                }

                .scp-component { 
                    border: 2px dashed #ccc; padding: 20px; margin: 20px 0; 
                    background: #fdfdfd; position: relative; border-radius: 8px;
                    color: #444; font-size: 14px; cursor: pointer;
                }

                /* --- AIM 渲染样式 --- */
                .aim-box {
                    border: 1px solid #ddd; background: #fff; padding: 0;
                    margin: 20px 0; font-family: 'Segoe UI', sans-serif;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05); cursor: default;
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

                /* 处理长链接，防止撑开布局 */
                [data-field="name"] {
                    word-break: break-all;
                    min-width: 50px; 
                    display: inline-block; 
                    border-bottom: 1px dashed #ccc;
                }

                /* --- Tab View 样式 --- */
                .tabview-box { border: 1px solid #ccc; background: #fff; display: flex; flex-direction: column; overflow: hidden; }
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
                .collapsible-box { border: 1px solid #aaa; background: #f9f9f9; padding: 0; margin: 15px 0; border-radius: 4px; overflow: hidden; width: 100%; box-sizing: border-box; }
                .collapsible-header { display: flex; gap: 15px; background: #e0e0e0; padding: 8px 15px; font-size: 12px; color: #333; cursor: pointer; align-items: center; border-bottom: 1px solid #ccc; }
                .title-label { font-weight: bold; color: #901111; }
                .title-input { border-bottom: 1px dashed #666; padding: 0 5px; outline: none; min-width: 60px; color: #000; background: #fff; }
                .collapsible-content-area { padding: 15px; background: #fff; min-height: 40px; cursor: text; display: none; }
                .collapsible-box.open .collapsible-content-area { display: block; }

                /* --- 授权引用修复样式 --- */
                .license-box { border: 1px solid #901111; padding: 0; background: #fff; font-size: 13px; color: #333; overflow: hidden; width: 100%; box-sizing: border-box; }
                .license-header { color: #901111; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: space-between; padding: 8px 15px; background: #fdfdfd; }
                .license-header::after { content: '▼'; font-size: 10px; margin-left: 10px; }
                .license-box.open .license-header::after { content: '▲'; }
                .license-content { display: none; padding: 15px; line-height: 1.8; }
                .license-box.open .license-content { display: block; }
                .license-field-row { margin-bottom: 4px; border-bottom: 1px dotted #eee; }
                .field-label { font-weight: bold; color: #666; width: 80px; display: inline-block; }
                .editable-field { color: #b01; font-weight: bold; padding: 0 4px; outline: none; min-width: 50px; display: inline-block; border-bottom: 1px dashed #ccc; }
                .editable-field:empty::before { content: " (点击输入) "; color: #ccc; font-weight: normal; font-style: italic; }
                .extra-files-container { border-top: 2px dashed #901111; margin-top: 10px; padding-top: 10px; }
                .file-entry { border: 1px solid #ccc; background: #f9f9f9; padding: 10px; margin-bottom: 10px; border-radius: 4px; position: relative; }
                .btn-add-file { background: #901111; color: white; border: none; padding: 8px 16px; cursor: pointer; font-size: 14px; margin-top: 5px; border-radius: 4px; }
                .btn-del-file { position: absolute; top: 2px; right: 5px; color: red; cursor: pointer; font-weight: bold; border: none; background: none; font-size: 20px; }

                /* ACS 样式 */
                .acs-box { border-left: 12px solid var(--acs-color, #f1c40f); text-align: left; background: #f9f9f9; padding: 15px 20px; display: flex; flex-direction: column; gap: 8px; font-family: 'Segoe UI', sans-serif; transition: all 0.3s ease; }
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

                .scp-footnote { color: #B22222 !important; font-weight: bold; vertical-align: super; font-size: 0.8em; cursor: pointer; user-select: none; margin: 0 2px; }
                #footnote-list-footer { margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; font-size: 0.9em; color: #555; }
                .footnote-list-item { margin-bottom: 5px; }
                .footnote-content { outline: none; border-bottom: 1px dashed transparent; }
                .footnote-content:focus { border-bottom: 1px dashed #999; background: #fffdf0; }

                .scp-hr { height: 40px; border: 1px dashed transparent; display: flex; align-items: center; justify-content: center; position: relative; }
                .scp-hr::after { content: ""; width: 100%; height: 2px; background: #333; display: block; }
                .scp-hr:hover { border: 1px dashed #901111; background: rgba(144, 17, 17, 0.05); }

                .size-span { display: inline; }
            </style>
            <script>
                const COLOR_MAP = {
                    'safe': '#27ae60', 'euclid': '#f1c40f', 'keter': '#c0392b',
                    'thaumiel': '#16a085', 'apollyon': '#5d001e',
                    'neutralized': '#7f8c8d', 'esoteric': '#9b59b6'
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

                function toggleImgControls(btn) {
                    const box = btn.closest('.image-block-box');
                    box.classList.toggle('img-controls-hidden');
                }

                // Paste handler for cleaning links
                document.addEventListener('paste', function(e) {
                    // Check if the target is a data-field="name" inside an image block
                    const target = e.target;
                    // Use .closest to check if we are inside the name field or its children
                    if (target.matches('.image-block-box [data-field="name"]') || target.closest('.image-block-box [data-field="name"]')) {
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

                    // Update size
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
                        if (table.style.borderStyle === 'dashed' || table.getAttribute('border') === '0') {
                            table.setAttribute('border', '1');
                            table.style.borderStyle = 'solid';
                            table.classList.remove('no-border');
                        } else {
                            table.setAttribute('border', '0');
                            table.style.borderStyle = 'dashed';
                            table.classList.add('no-border');
                        }
                    }
                }

                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Backspace') {
                        const sel = window.getSelection();
                        if (!sel.rangeCount || !sel.isCollapsed) return;
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

                function setupObserver() {
                    const editor = document.getElementById('editor-root');
                    const observer = new MutationObserver((mutations) => {
                        let needsRefresh = false;
                        mutations.forEach((mutation) => {
                            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                                handleTitleMarkdown();
                                needsRefresh = true;
                            }
                        });
                        if (needsRefresh && !document.activeElement.closest('#footnote-list-footer')) {
                            refreshFootnotes();
                        }
                    });
                    observer.observe(editor, { childList: true, characterData: true, subtree: true });
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
                        const match = text.match(/^(\+{1,6})\s+(.*)/);
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
                    if (footnotes[index]) footnotes[index].setAttribute('data-content', el.innerText);
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
                    }
                }

                function addLicenseFile(btn) {
                    const container = btn.previousElementSibling;
                    const div = document.createElement('div');
                    div.className = 'file-entry';
                    div.innerHTML = `<button class="btn-del-file" onclick="this.parentElement.remove()">×</button><div class="license-field-row"><span class="field-label">文件名：</span><span class="editable-field" data-field="file_name" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">图像名：</span><span class="editable-field" data-field="img_name" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">图像作者：</span><span class="editable-field" data-field="img_author" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">授权协议：</span><span class="editable-field" data-field="img_license" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">来源链接：</span><span class="editable-field" data-field="source_link" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">衍生自：</span><span class="editable-field" data-field="derived_from" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">备注：</span><span class="editable-field" data-field="note" contenteditable="true"></span></div>`;
                    container.appendChild(div);
                }

                document.addEventListener('click', function(e) {
                    const licHeader = e.target.closest('.license-header');
                    if (licHeader) { licHeader.parentElement.classList.toggle('open'); return; }
                    const colHeader = e.target.closest('.collapsible-header');
                    if (colHeader && !e.target.closest('.title-input')) { colHeader.parentElement.classList.toggle('open'); }
                });

                document.addEventListener('input', function(e) {
                    if (e.target.closest('#editor-root')) { }
                });

                window.onload = function() {
                    setupObserver();
                    refreshFootnotes();
                };
            </script>
        </head>
        <body>
            <div class="rate-module-box" contenteditable="false">[[module Rate]]</div>
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
        # 启用/禁用子选项
        self.basalt_sub_options_frame.setEnabled(checked)
        # 更新状态
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

    def exec_format(self, command, value=None):
        self.browser.page().runJavaScript(f"document.execCommand('{command}', false, {json.dumps(value)});")
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
            '<div class="scp-component" data-type="toc" contenteditable="false" style="border: 1px dashed #999; padding: 5px; background: #f0f0f0;"><b>目录 (TOC)</b><br>[[toc]]</div>')

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
            html = f'''<div class="scp-component aim-box" data-type="aim" {blocks_attr} contenteditable="false"><table class="aim-table"><tr {row_style_top}><td colspan="2"><div class="aim-label">项目编号</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">SCP-XXXX</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">等级 / 公开</div><div class="aim-value" data-field="lv" contenteditable="true">等级-01/公开</div></td></tr><tr {row_style_top}><td colspan="2"><div class="aim-label">收容等级</div><div class="aim-value" data-field="cc" contenteditable="true">THAUMIEL</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">扰动等级</div><div class="aim-value" data-field="dc" contenteditable="true">DARK</div></td></tr><tr {row_style_bottom} style="text-align: center; background: #fafafa;"><td><div class="aim-label">负责站点</div><div class="aim-value" data-field="site" contenteditable="true">Site-0</div></td><td><div class="aim-label">站点主管</div><div class="aim-value" data-field="dir" contenteditable="true">Dr 主管</div></td><td><div class="aim-label">首席研究员</div><div class="aim-value" data-field="head" contenteditable="true">Dr 博士</div></td><td><div class="aim-label">指派特遣队</div><div class="aim-value" data-field="mtf" contenteditable="true">Alpha-1</div></td></tr></table><div class="aim-footer">{footer_text}</div></div>'''

        elif comp == "图片块 (Image Block)":
            # 增加 .img-toggle-btn 用于隐藏/显示控制栏，包裹 input 和 buttons 在 .img-controls-wrapper 中
            # 移除了居中按钮，并添加了 clear:both 的 div 以便布局隔离
            # 增加前后 &nbsp; 锚点以允许光标选中
            html = '''<span>&nbsp;</span><div class="scp-component image-block-box" data-type="image-block" data-align="right" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div><div style="background:#fff; padding:5px; text-align:center; border-bottom:1px solid #eee; font-size:0.9em;"><b>源:</b> <span data-field="name" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:50px; display:inline-block; border-bottom:1px dashed #ccc;">link/to/image.jpg</span></div></div><div class="image-block-content"><img src="" class="img-preview" style="max-width:100%; display:none; margin:0 auto 5px auto;"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">在此输入图片描述</span></div></div><span>&nbsp;</span><div style="clear:both;"></div>'''

        elif comp == "高级图片块 (Advanced Image)":
            # 移除开头的 &nbsp; 锚点，防止生成多余空格
            html = '''<div class="scp-component image-block-box" data-type="image-block-adv" data-align="right" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div><div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div><b>源:</b> <span data-field="name" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:50px; display:inline-block; border-bottom:1px dashed #ccc;">link/to/image.jpg</span></div><div><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span> <b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span></div></div></div><div class="image-block-content"><img src="" class="img-preview" style="max-width:100%; display:none; margin:0 auto 5px auto;"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">在此输入图片描述</span></div></div><span>&nbsp;</span><div style="clear:both;"></div>'''

        elif "Tab View" in comp:
            html = '''<div class="scp-component tabview-box" data-type="tabview" contenteditable="false"><div class="tab-header"><span class="tab-btn active" onclick="selectTab(this)" contenteditable="true">Tab 1</span><span class="tab-btn" onclick="selectTab(this)" contenteditable="true">Tab 2</span><span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents"><div class="tab-item active" contenteditable="true"><p>Tab 1 Content...</p></div><div class="tab-item" contenteditable="true"><p>Tab 2 Content...</p></div></div></div>'''

        elif "User" in comp:
            html = '''<span class="scp-component user-tag" data-type="user" contenteditable="false"><div class="user-icon"></div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">User Name</span></span>'''

        elif comp == "高级用户信息 (Advanced User)":
            html = '''<span class="scp-component user-tag" data-type="user-adv" contenteditable="false"><div class="user-icon" style="background:gold; text-align:center; line-height:12px; font-size:10px; color:#fff;">★</div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">User Name</span></span>'''

        elif "ACS" in comp:
            html = '''<div class="scp-component acs-box" data-type="acs" data-clearance="2" data-container="euclid" data-secondary="none" data-disruption="vlam" data-risk="notice" style="--acs-color: #f1c40f;" contenteditable="false"><div class="acs-header-row" contenteditable="false"><div class="acs-title">SCP-CN 异常分级栏</div><div class="acs-anim-toggle"><span>动画:</span><label class="switch"><input type="checkbox" class="acs-anim-checkbox"><span class="slider"></span></label></div><div class="acs-item-num" contenteditable="true" data-field="item-number">SCP-CN-XXXX</div></div><div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px;"><div><small style="color:#888; font-size:9px; text-transform:uppercase;">许可等级</small><br><b data-field="clearance" contenteditable="true">2级</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">项目等级</small><br><b data-field="container" style="color:var(--acs-color)" contenteditable="true">Euclid</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">扰动等级</small><br><b data-field="disruption" contenteditable="true">Vlam</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">风险等级</small><br><b data-field="risk" contenteditable="true">Notice</b></div></div></div><p><br></p>'''

        elif "折叠块" in comp:
            html = '''<div class="scp-component collapsible-box open" data-type="collapsible" contenteditable="false"><div class="collapsible-header"><span><span class="title-label">显示标题:</span> <span class="title-input" data-field="show" contenteditable="true">+ 打开折叠内容</span></span><span><span class="title-label">隐藏标题:</span> <span class="title-input" data-field="hide" contenteditable="true">- 关闭折叠内容</span></span></div><div class="collapsible-content-area" contenteditable="true"><p>在这里输入折叠内的内容...</p></div></div>'''

        elif "授权引用" in comp:
            html = '''<div class="scp-component license-box open" data-type="license" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)</div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true"></span></div><div class="license-field-row"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true"></span></div><hr><div class="extra-files-container"></div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>'''
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
                    range.setStartAfter(fragment.lastChild);
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
        js_table = f"!!document.elementFromPoint({pos.x()}, {pos.y()}).closest('table')"
        js_tab_btn = f"!!document.elementFromPoint({pos.x()}, {pos.y()}).classList.contains('tab-btn')"

        full_js = f"JSON.stringify({{ comp: {js}, table: {js_table}, tabBtn: {js_tab_btn} }})"
        self.browser.page().runJavaScript(full_js, lambda res: self.show_menu(pos, json.loads(res)))

    def show_menu(self, pos, res):
        menu = QMenu()
        c_type = res.get('comp')
        in_table = res.get('table')
        is_tab_btn = res.get('tabBtn')

        # 增加通用粘贴选项 (因为接管了右键菜单，默认粘贴可能失效)
        paste_act = menu.addAction("粘贴")
        paste_act.triggered.connect(lambda: self.browser.page().triggerAction(QWebEnginePage.WebAction.Paste))
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
                cm = menu.addMenu("修改等级颜色")
                for cls in ["Safe", "Euclid", "Keter", "Thaumiel", "Apollyon", "Neutralized"]:
                    act = cm.addAction(cls)
                    act.triggered.connect(lambda checked, c=cls: self.change_acs_class(pos, c))

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

    def change_acs_class(self, pos, class_name):
        self.browser.page().runJavaScript(
            f'applyAcsChange(document.elementFromPoint({pos.x()}, {pos.y()}), "{class_name}")')

    def edit_footnote_at_pos(self, pos):
        js = f"var el = document.elementFromPoint({pos.x()}, {pos.y()}); while(el && !el.classList.contains('scp-footnote')) el = el.parentElement; el ? el.getAttribute('data-content') : ''"

        def on_got(content):
            new_text, ok = QInputDialog.getMultiLineText(self, "编辑脚注", "内容:", content)
            if ok: self.browser.page().runJavaScript(
                f"var el = document.elementFromPoint({pos.x()}, {pos.y()}); while(el && !el.classList.contains('scp-footnote')) el = el.parentElement; if(el) {{ el.setAttribute('data-content', {json.dumps(new_text)}); refreshFootnotes(); }}")

        self.browser.page().runJavaScript(js, on_got)

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
                if blocks != '!':
                    code += f"|XXXX={f('xxxx')}\n|lv={f('lv')}\n|cc={f('cc')}\n|dc={f('dc')}\n"
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
                def get_field_lic(n, field):
                    el = n.select_one(f'[data-field="{field}"]')
                    return el.get_text().strip() if el else ""

                author = get_field_lic(node, "author")
                translator = get_field_lic(node, "translator")

                use_bf = state.get('better_footnotes', False)
                fn_block = "" if use_bf else "[[footnoteblock]]\n"

                base_code = f"{fn_block}=====\n[[include :scp-wiki-cn:component:license-box\n|author={author}\n|translator={translator}\n]]\n"

                files_code = ""
                file_entries = node.select('.file-entry')
                for i, entry in enumerate(file_entries):
                    # Multi-file loop fix: add newline between entries (but not > char)
                    if i > 0:
                        files_code += "\n"

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
                            files_code += f"> **{label}**{val}\n"
                    files_code += ">\n"

                return base_code + files_code + "[[include :scp-wiki-cn:component:license-box-end]]\n=====\n"

            if c_type == 'acs':
                item = safe_get('[data-field="item-number"]')
                clr = (re.search(r'\d+', safe_get('[data-field="clearance"]')) or re.search(r'\d+', '1')).group()
                cnt = safe_get('[data-field="container"]').lower()
                dsr = safe_get('[data-field="disruption"]').lower()
                rsk = safe_get('[data-field="risk"]').lower()

                anim = ""
                checkbox = node.select_one('.acs-anim-checkbox')
                if checkbox and checkbox.has_attr('checked'):
                    anim = "[[include :scp-wiki-cn:component:acs-animation]]\n"

                return f"\n{anim}[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number={item}\n|clearance={clr}\n|container-class={cnt}\n|disruption-class={dsr}\n|risk-class={rsk}\n]]\n"

            if c_type == 'toc':
                return "\n[[toc]]\n"

            if c_type == 'footnote':
                content = node.get('data-content', '').strip()
                if state.get('better_footnotes', False):
                    return f'[[span class="fnnum"]].[[/span]][[span class="fncon"]]{content}[[/span]]'
                else:
                    return f" [[footnote]] {content} [[/footnote]] "

            if c_type == 'hr': return "\n------\n"

        # 处理表格导出
        if node.name == 'table':
            rows_code = []
            for tr in node.find_all('tr'):
                cells_code = ""
                for cell in tr.find_all(['td', 'th']):
                    prefix = "||"
                    colspan = int(cell.get('colspan', 1))
                    if colspan > 1:
                        prefix += "||" * (colspan - 1)

                    cell_content = "".join(self.parse_node(c, state) for c in cell.contents).strip()
                    cell_content = cell_content.replace('\n', ' _\n')

                    if cell.name == 'th':
                        cells_code += f"{prefix}~ {cell_content} "
                    else:
                        cells_code += f"{prefix} {cell_content} "
                rows_code.append(cells_code + "||")
            return "\n" + "\n".join(rows_code) + "\n"

        # 递归处理子节点
        content = "".join(self.parse_node(child, state) for child in node.contents)
        tag = node.name

        # --- 强制换行符逻辑 ---
        if tag == 'p' and not content.strip() and node.find('br'):
            return "\n@@@@\n"

        # Check for alignment style
        style = node.get('style', '')
        align_mark = ""
        if 'text-align: right' in style or 'text-align:right' in style:
            align_mark = ">"
        elif 'text-align: left' in style or 'text-align:left' in style:
            align_mark = "<"
        elif 'text-align: center' in style or 'text-align:center' in style:
            align_mark = "="

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            h_code = f"\n{'+' * int(tag[1])} {content.strip()}\n"
            if align_mark: return f"[[{align_mark}]]\n{h_code.strip()}\n[[/{align_mark}]]\n"
            return h_code

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
            size_match = re.search(r'font-size:\s*([\w\.-]+)', style)
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
            lines = content.strip().split('\n')
            res = ""
            for line in lines:
                if line.strip():
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

            return f"[[[{prefix}{href} | {text}]]]"

        # Fixed P tag handling to remove extra leading newline
        if tag == 'p':
            val = f"{content}\n"
            if align_mark: return f"[[{align_mark}]]\n{content.strip()}\n[[/{align_mark}]]\n"
            return val

        if tag == 'div' and align_mark:
            return f"[[{align_mark}]]\n{content.strip()}\n[[/{align_mark}]]\n"

        if tag == 'br': return " @@@@ "
        if tag in ['b', 'strong']: return f"**{content}**"
        if tag in ['i', 'em']: return f"//{content}//"
        return content

    def process_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        root = soup.find(id="editor-root")
        if not root: return

        final_code = "[[module Rate]]\n"

        # 1. 插入全局版式 (基于内部状态，而非DOM)
        self.update_theme_state()

        if self.page_theme_config["type"] == "basalt":
            options = self.page_theme_config["options"]
            if options:
                final_code += f"[[include :scp-wiki-cn:theme:basalt 版式设置|{'|'.join(options)}]]\n"
            else:
                final_code += "[[include :scp-wiki-cn:theme:basalt]]\n"

        # 2. 插入 Better Footnotes
        if self.use_better_footnotes:
            final_code += "[[include :scp-wiki-cn:component:betterfootnotes]]\n"

        # 3. 准备解析状态
        parse_state = {'better_footnotes': self.use_better_footnotes}

        # 4. 解析正文 (Natural order)
        raw_body = self.parse_node(root, parse_state)

        # 5. 后处理
        body = raw_body.replace('\r\n', '\n')
        body = re.sub(r'\n{3,}', '\n\n@@@@\n\n', body)

        final_code += body

        self.source_display.setPlainText(final_code.strip())
        self.centralWidget().findChild(QTabWidget).setCurrentIndex(1)

    def fetch_source(self):
        url = self.url_input.text()
        if not url: return
        try:
            res = requests.get(url + "/code/1")
            if res.status_code == 200: self.source_display.setPlainText(
                BeautifulSoup(res.text, 'html.parser').find('pre').text)
        except:
            QMessageBox.warning(self, "错误", "无法获取源码。")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SCPEditor()
    window.show()
    sys.exit(app.exec())