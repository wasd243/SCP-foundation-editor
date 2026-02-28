from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QLabel, QToolBar, QMenu, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup, QDockWidget, QFrame, QScrollArea, QToolButton, QSplitter,
    QTabWidget  # <--- 就是加了这一个
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont

from ui.widgets.CustomControlls import PlainPasteTextEdit, CustomWebPage
from css_styles.html_template import EDITOR_HTML

def setup_main_ui(window):
    """
    负责构建主窗口的所有 UI 元素。
    window: 传入的 SCPEditor 主窗口实例 (相当于原来的 self)
    """
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)

    # --- 全局样式设置 ---
    window.setStyleSheet("""
        QPushButton { font-size: 14px; min-height: 40px; border-radius: 4px; padding: 5px 15px; }
        QComboBox { min-height: 35px; font-size: 13px; }
        QLineEdit { min-height: 35px; font-size: 13px; }
        QLabel { font-size: 13px; }
        QDockWidget { font-size: 13px; }
        QGroupBox { font-weight: bold; border: 1px solid #aaa; margin-top: 10px; padding-top: 10px; }
        QToolBar QToolButton { width: 40px; height: 30px; font-size: 16px; font-weight: bold; margin: 2px; border: 1px solid transparent; border-radius: 3px; }
        QToolBar QToolButton:hover { background-color: #e0e0e0; border: 1px solid #ccc; }
        QToolBar QToolButton:checked { background-color: #cce5ff; border: 1px solid #0056b3; color: #000; }
    """)

    # --- 工具栏 ---
    toolbar = QToolBar("格式工具栏")
    toolbar.setStyleSheet("QToolBar { icon-size: 24px; spacing: 5px; }")
    main_layout.addWidget(toolbar)

    window.heading_selector = QComboBox()
    window.heading_selector.addItems(["正文 (P)", "标题 1 (+)", "标题 2 (++)", "标题 3 (+++)", "标题 4 (++++)", "标题 5 (+++++)", "标题 6 (++++++)"])
    window.heading_selector.setMinimumWidth(120)
    window.heading_selector.currentIndexChanged.connect(window.set_heading)
    toolbar.addWidget(window.heading_selector)
    toolbar.addSeparator()

    save_action = QAction("💾", window)
    save_action.setToolTip("保存文档到桌面")
    save_action.triggered.connect(window.initiate_save)
    toolbar.addAction(save_action)
    toolbar.addSeparator()

    # 格式化按钮
    window.bold_act = QAction("B", window)
    window.bold_act.setToolTip("加粗 (Bold) [关闭]")
    bold_font = QFont()
    bold_font.setBold(True)
    window.bold_act.setFont(bold_font)
    window.bold_act.setCheckable(True)
    window.bold_act.triggered.connect(lambda: window.exec_format("bold"))
    toolbar.addAction(window.bold_act)

    window.italic_act = QAction("I", window)
    window.italic_act.setToolTip("斜体 (Italic) [关闭]")
    italic_font = QFont()
    italic_font.setItalic(True)
    window.italic_act.setFont(italic_font)
    window.italic_act.setCheckable(True)
    window.italic_act.triggered.connect(lambda: window.exec_format("italic"))
    toolbar.addAction(window.italic_act)

    window.underline_act = QAction("U", window)
    window.underline_act.setToolTip("下划线 (Underline) [关闭]")
    underline_font = QFont()
    underline_font.setUnderline(True)
    window.underline_act.setFont(underline_font)
    window.underline_act.setCheckable(True)
    window.underline_act.triggered.connect(lambda: window.exec_format("underline"))
    toolbar.addAction(window.underline_act)

    window.strike_act = QAction("S", window)
    window.strike_act.setToolTip("删除线 (Strikethrough) [关闭]")
    strike_font = QFont()
    strike_font.setStrikeOut(True)
    window.strike_act.setFont(strike_font)
    window.strike_act.setCheckable(True)
    window.strike_act.triggered.connect(lambda: window.exec_format("strikeThrough"))
    toolbar.addAction(window.strike_act)
    toolbar.addSeparator()

    window.sup_act = QAction("x²", window)
    window.sup_act.setToolTip("上标 (Superscript) [关闭]")
    window.sup_act.setCheckable(True)
    window.sup_act.triggered.connect(lambda: window.exec_format("superscript"))
    toolbar.addAction(window.sup_act)

    window.sub_act = QAction("x₂", window)
    window.sub_act.setToolTip("下标 (Subscript) [关闭]")
    window.sub_act.setCheckable(True)
    window.sub_act.triggered.connect(lambda: window.exec_format("subscript"))
    toolbar.addAction(window.sub_act)

    window.mono_act = QAction("M", window)
    window.mono_act.setToolTip("等宽字体 (Monospace) [关闭]")
    mono_font = QFont("Courier New")
    window.mono_act.setFont(mono_font)
    window.mono_act.setCheckable(True)
    window.mono_act.triggered.connect(lambda: window.browser.page().runJavaScript("toggleMonospace();"))
    toolbar.addAction(window.mono_act)
    toolbar.addSeparator()

    window.color_act = QAction("A", window)
    window.color_act.setToolTip("文字颜色")
    window.color_act.setCheckable(True)
    color_menu = QMenu(window)
    color_menu.addAction("选择颜色 (Choose Color)").triggered.connect(window.choose_color)
    color_menu.addAction("清除颜色 (Clear Color)").triggered.connect(window.clear_color)
    window.color_act.setMenu(color_menu)
    toolbar.addAction(window.color_act)

    color_btn = toolbar.widgetForAction(window.color_act)
    if color_btn:
        color_btn.setStyleSheet("color: red; font-weight: bold;")
        color_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

    toolbar.addAction(QAction("🔗", window, toolTip="插入链接", triggered=window.open_link_dialog))
    toolbar.addSeparator()

    window.ul_act = QAction("• List", window, toolTip="无序列表", checkable=True)
    window.ul_act.triggered.connect(lambda: window.exec_format("insertUnorderedList"))
    toolbar.addAction(window.ul_act)

    window.ol_act = QAction("1. List", window, toolTip="有序列表", checkable=True)
    window.ol_act.triggered.connect(lambda: window.exec_format("insertOrderedList"))
    toolbar.addAction(window.ol_act)

    toolbar.addAction(QAction("❝❞", window, toolTip="引用块", triggered=lambda: window.exec_format("formatBlock", "blockquote")))
    toolbar.addSeparator()

    toolbar.addAction(QAction("——", window, toolTip="分割线", triggered=window.insert_hr))
    toolbar.addAction(QAction("⊞", window, toolTip="表格", triggered=window.insert_table))
    toolbar.addAction(QAction("音频", window, toolTip="音频播放器", triggered=window.insert_audio))
    toolbar.addAction(QAction("TOC", window, toolTip="目录", triggered=window.insert_toc))

    window.left_act = QAction("⇐", window, toolTip="靠左 [关闭]", checkable=True)
    window.left_act.triggered.connect(lambda: window.exec_format("justifyLeft"))
    toolbar.addAction(window.left_act)

    window.right_act = QAction("⇒", window, toolTip="靠右 [关闭]", checkable=True)
    window.right_act.triggered.connect(lambda: window.exec_format("justifyRight"))
    toolbar.addAction(window.right_act)

    toggle_dock_action = QAction("⚙️", window, toolTip="显示/隐藏页面属性", checkable=True, checked=True)
    toggle_dock_action.triggered.connect(window.toggle_right_dock)
    toolbar.addAction(toggle_dock_action)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    main_layout.addWidget(splitter)

    # --- 左侧面板 ---
    left_panel = QTabWidget()
    left_panel.setStyleSheet("QTabBar::tab { height: 35px; width: 100px; font-size: 13px; }")

    window.comp_scroll = QScrollArea()
    window.comp_scroll.setWidgetResizable(True)
    window.comp_scroll.setStyleSheet("QScrollArea { border: none; }")
    comp_tab = QWidget()
    comp_layout = QVBoxLayout(comp_tab)
    window.comp_scroll.setWidget(comp_tab)

    # 相对字号
    comp_layout.addWidget(QLabel("<b>相对字号设置:</b>"))
    rel_size_layout = QHBoxLayout()
    window.rel_size_selector = QComboBox()
    window.rel_size_selector.addItems(["smaller", "larger", "80%", "100%", "120%", "150%", "200%", "0.8em", "1em", "1.2em", "1.5em", "2em", "自定义"])
    apply_rel_size_btn = QPushButton("应用")
    apply_rel_size_btn.clicked.connect(window.apply_relative_size)
    rel_size_layout.addWidget(window.rel_size_selector)
    rel_size_layout.addWidget(apply_rel_size_btn)
    comp_layout.addLayout(rel_size_layout)

    # 绝对字号
    comp_layout.addWidget(QLabel("<b>绝对字号设置:</b>"))
    size_layout = QHBoxLayout()
    window.size_selector = QComboBox()
    window.size_selector.addItems(["xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large", "自定义px"])
    apply_size_btn = QPushButton("应用字号")
    apply_size_btn.clicked.connect(lambda: window.apply_font_size())
    size_layout.addWidget(window.size_selector)
    size_layout.addWidget(apply_size_btn)
    comp_layout.addLayout(size_layout)

    # 玄武岩版式专用代码
    window.basalt_extra_group = QGroupBox("玄武岩版式专用代码 (需启用玄武岩)")
    window.basalt_extra_group.setVisible(False)
    basalt_extra_layout = QVBoxLayout()
    basalt_comps = [
        ("引用/笔记模块", "blockquote", "background-color: #f8f9fa; border: 1px solid #dee2e6;"),
        ("高级引用/笔记模块", "notation", "background-color: #f1f3f5; border-left: 5px solid #ced4da;"),
        ("虚线框", "jotting", "background-color: #f8f9fa; border: 1px dashed #ced4da;"),
        ("调试用笔记模块", "modal", "background-color: #ffffff; border: 1px solid #ced4da;"),
        ("小号调试用笔记模块", "smallmodal", "background-color: #ffffff; border: 1px solid #e9ecef;"),
        ("笔记模块", "papernote", "background-color: #e9ecef; border: none;"),
        ("浮动框 (左)", "floatbox", "background-color: #f4f4f4; border: 1px solid #ddd;"),
        ("浮动框 (右)", "floatbox right", "background-color: #f4f4f4; border: 1px solid #ddd;"),
        ("白色文件模板", "document", "background-color: #fff; border: 1px solid #eee;"),
        ("黑色文件模板", "darkdocument", "background-color: #1a1a1a; border: 1px solid #333; color: white;"),
        ("RAISA备忘录", "raisa_memo", "background-color: #fef3c7; border: 1px solid #f59e0b;"),
        ("分级委员会备忘录", "classification_memo", "background-color: #ecfdf5; border: 1px solid #10b981;"),
        ("潜在威胁响应局通知", "ettra_memo", "background-color: #fef2f2; border: 1px solid #ef4444;"),
        ("伦理委员会备忘录", "ethics_memo", "background-color: #fff7ed; border: 1px solid #f97316;"),
        ("时间异常部门备忘录", "temporal_memo", "background-color: #f8fafc; border: 1px solid #64748b;"),
        ("监督者指挥部备忘录", "overwatch_memo", "background-color: #f1f5f9; border: 1px solid #475569;"),
        ("误传部门通知", "miscomm_memo", "background-color: #f5f3ff; border: 1px solid #8b5cf6;")
    ]
    for label, cls, style in basalt_comps:
        btn = QPushButton(label)
        btn.setToolTip(f"[[div class=\"{cls}\"]]")
        btn.setStyleSheet(f"height: 45px; font-family: 'Courier New', monospace; font-size: 14px; text-align: center; color: #333; {style}")
        btn.clicked.connect(lambda checked, c=cls: window.insert_basalt_div(c))
        basalt_extra_layout.addWidget(btn)
    window.basalt_extra_group.setLayout(basalt_extra_layout)
    comp_layout.addWidget(window.basalt_extra_group)

    comp_layout.addWidget(QLabel("<br><b>选择维基组件:</b>"))
    window.comp_selector = QComboBox()
    window.comp_selector.addItems([
        "ACS 分级系统", "AIM 高级信息方法论", "折叠块 (Collapsible)", "CSS 模块",
        "DIV 模块", "脚注 (Footnote)", "版式", "图片块 (Image Block)",
        "高级图片块 (Advanced Image)", "Tab View (选项卡)", "用户标签 (User)",
        "高级用户信息 (Advanced User)", "授权引用 (License Box)"
    ])
    window.comp_selector.currentIndexChanged.connect(window.toggle_config_panels)
    comp_layout.addWidget(window.comp_selector)

    # --- 版式配置 ---
    window.basalt_group = QGroupBox("版式与全局设置")
    window.basalt_group.setVisible(False)
    basalt_vbox = QVBoxLayout()
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.Shape.NoFrame)
    scroll_content = QWidget()
    scroll_layout = QVBoxLayout(scroll_content)
    scroll_layout.setContentsMargins(0, 0, 0, 0)

    window.check_better_footnotes = QCheckBox("启用 Better Footnotes (更好的脚注)")
    window.check_better_footnotes.setStyleSheet("color: red; font-weight: bold; font-size: 13px; padding: 5px;")
    scroll_layout.addWidget(window.check_better_footnotes)

    window.check_enable_basalt = QCheckBox("启用玄武岩主题")
    window.check_enable_basalt.toggled.connect(window.on_basalt_toggled)
    scroll_layout.addWidget(window.check_enable_basalt)

    window.basalt_sub_options_frame = QFrame()
    window.basalt_sub_options_frame.setEnabled(False)
    sub_layout = QVBoxLayout(window.basalt_sub_options_frame)
    sub_layout.setContentsMargins(20, 0, 0, 0)
    window.check_dark = QCheckBox("暗色模式 (darkmode)")
    window.check_wide = QCheckBox("加宽页面 (wide)")
    window.check_hidetitle = QCheckBox("隐藏标题 (hidetitle)")
    cb_style = "QCheckBox { font-size: 13px; spacing: 8px; padding: 3px; }"
    for cb in [window.check_enable_basalt, window.check_dark, window.check_wide, window.check_hidetitle]: cb.setStyleSheet(cb_style)
    sub_layout.addWidget(window.check_dark)
    sub_layout.addWidget(window.check_wide)
    sub_layout.addWidget(window.check_hidetitle)
    scroll_layout.addWidget(window.basalt_sub_options_frame)

    shivering_sep = QFrame()
    shivering_sep.setFrameShape(QFrame.Shape.HLine)
    scroll_layout.addWidget(shivering_sep)

    window.check_enable_shivering = QCheckBox("启用夜琉璃版式")
    window.check_enable_shivering.setStyleSheet(cb_style)
    window.check_enable_shivering.toggled.connect(window.on_shivering_toggled)
    scroll_layout.addWidget(window.check_enable_shivering)

    window.shivering_sub_options_frame = QFrame()
    window.shivering_sub_options_frame.setEnabled(False)
    shivering_sub_layout = QVBoxLayout(window.shivering_sub_options_frame)
    shivering_sub_layout.setContentsMargins(20, 0, 0, 0)

    window.shivering_city_group = QButtonGroup(window)
    window.radio_shiv_default = QRadioButton("默认")
    window.radio_shiv_mo = QRadioButton("澳门 (Macau)")
    window.radio_shiv_kl = QRadioButton("吉隆坡 (Kuala Lumpur)")
    window.radio_shiv_dub = QRadioButton("都柏林 (Dublin)")
    window.radio_shiv_ct = QRadioButton("开普敦 (Cape Town)")
    window.radio_shiv_ba = QRadioButton("布宜诺斯艾利斯 (Buenos Aires)")
    rb_style = "QRadioButton { font-size: 13px; spacing: 8px; padding: 3px; }"
    for rb in [window.radio_shiv_default, window.radio_shiv_mo, window.radio_shiv_kl, window.radio_shiv_dub, window.radio_shiv_ct, window.radio_shiv_ba]:
        rb.setStyleSheet(rb_style)
        window.shivering_city_group.addButton(rb)
        shivering_sub_layout.addWidget(rb)
        rb.toggled.connect(window.update_theme_state)
    window.radio_shiv_default.setChecked(True)
    scroll_layout.addWidget(window.shivering_sub_options_frame)

    bhl_sep = QFrame()
    bhl_sep.setFrameShape(QFrame.Shape.HLine)
    scroll_layout.addWidget(bhl_sep)

    window.check_enable_bhl = QCheckBox("启用黑色标记笔 (Black Highlighter)")
    window.check_enable_bhl.setStyleSheet(cb_style)
    window.check_enable_bhl.toggled.connect(window.on_bhl_toggled)
    scroll_layout.addWidget(window.check_enable_bhl)

    window.bhl_sub_options_frame = QFrame()
    window.bhl_sub_options_frame.setEnabled(False)
    bhl_sub_layout = QVBoxLayout(window.bhl_sub_options_frame)
    bhl_sub_layout.setContentsMargins(20, 0, 0, 0)
    window.check_dark_sidebar = QCheckBox("暗色侧边栏 (Dark Sidebar)")
    window.check_bhl_collapsible = QCheckBox("可折叠侧边栏 (Collapsible Sidebar)")
    window.check_bhl_toggle = QCheckBox("切换侧边栏 (Toggle Sidebar)")
    window.check_bhl_centered = QCheckBox("居中页眉 (Centered Header)")
    window.check_bhl_office = QCheckBox("办公室 (Office)")

    for cb in [window.check_dark_sidebar, window.check_bhl_collapsible, window.check_bhl_toggle, window.check_bhl_centered, window.check_bhl_office]:
        cb.setStyleSheet(cb_style)
        if cb == window.check_bhl_office: cb.toggled.connect(window.on_bhl_office_toggled)
        else: cb.toggled.connect(window.update_theme_state)
        bhl_sub_layout.addWidget(cb)
    scroll_layout.addWidget(window.bhl_sub_options_frame)

    scroll_area.setWidget(scroll_content)
    scroll_area.setMinimumHeight(400)
    scroll_area.setMaximumHeight(800) 
    basalt_vbox.addWidget(scroll_area)
    window.basalt_group.setLayout(basalt_vbox)
    comp_layout.addWidget(window.basalt_group)

    # --- AIM 配置 ---
    window.aim_group = QGroupBox("AIM 模块配置")
    window.aim_group.setVisible(False)
    aim_vbox = QVBoxLayout()
    window.aim_mode_group = QButtonGroup(window)
    window.radio_aim_full = QRadioButton("完整版头")
    window.radio_aim_top = QRadioButton("仅上半部分 (blocks=-)")
    window.radio_aim_bottom = QRadioButton("仅下半部分 (blocks=!)")
    for rb in [window.radio_aim_full, window.radio_aim_top, window.radio_aim_bottom]: rb.setStyleSheet(rb_style)
    window.radio_aim_full.setChecked(True)
    window.aim_mode_group.addButton(window.radio_aim_full)
    window.aim_mode_group.addButton(window.radio_aim_top)
    window.aim_mode_group.addButton(window.radio_aim_bottom)
    aim_vbox.addWidget(window.radio_aim_full)
    aim_vbox.addWidget(window.radio_aim_top)
    aim_vbox.addWidget(window.radio_aim_bottom)
    window.aim_group.setLayout(aim_vbox)
    comp_layout.addWidget(window.aim_group)

    insert_btn = QPushButton("应用/插入选定组件")
    insert_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; height: 50px; font-size: 16px; border-radius: 5px;")
    insert_btn.clicked.connect(window.insert_component)
    comp_layout.addWidget(insert_btn)

    export_btn = QPushButton("生成维基代码")
    export_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; height: 60px; font-size: 18px; margin-top: 15px; border-radius: 6px;")
    export_btn.clicked.connect(window.export_wikidot)
    comp_layout.addWidget(export_btn)

    window.check_auto_refresh = QCheckBox("保持刷新代码 (自动生成)")
    window.check_auto_refresh.setStyleSheet("font-size: 13px; font-weight: bold; padding: 5px; color: #d35400;")
    window.check_auto_refresh.stateChanged.connect(window.toggle_auto_refresh)
    comp_layout.addWidget(window.check_auto_refresh)

    window.auto_refresh_timer = QTimer(window)
    window.auto_refresh_timer.timeout.connect(window.export_wikidot)

    copy_btn = QPushButton("一键复制到剪切板")
    copy_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; height: 40px; margin-top: 5px; border-radius: 6px; font-size: 16px;")
    copy_btn.clicked.connect(window.copy_to_clipboard)
    comp_layout.addWidget(copy_btn)

    read_btn = QPushButton("读取桌面.txt文件到此")
    read_btn.setStyleSheet("background-color: #34495e; color: white; font-weight: bold; height: 40px; margin-top: 5px; border-radius: 6px; font-size: 16px;")
    read_btn.clicked.connect(window.read_from_desktop)
    comp_layout.addWidget(read_btn)

    clear_btn = QPushButton("一键清理所有内容")
    clear_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; height: 60px; font-size: 18px; margin-top: 15px; border-radius: 6px;")
    clear_btn.clicked.connect(window.clear_all_content)
    comp_layout.addWidget(clear_btn)

    comp_layout.addStretch()

    source_tab = QWidget()
    source_layout = QVBoxLayout(source_tab)
    import_btn = QPushButton(" 识别代码并生成界面 (Render to Editor)")
    import_btn.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; height: 40px; margin-top: 5px; border-radius: 6px;")
    import_btn.clicked.connect(window.render_to_editor)
    source_layout.addWidget(import_btn)

    window.source_display = PlainPasteTextEdit()
    window.source_display.setPlaceholderText("生成的维基代码将在此显示...")
    source_layout.addWidget(window.source_display)

    left_panel.addTab(window.comp_scroll, "编辑器")
    left_panel.addTab(source_tab, "代码视窗")

    window.browser = QWebEngineView()
    window.browser.setPage(CustomWebPage(window.browser, window))
    window.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    window.browser.customContextMenuRequested.connect(window.prepare_context_menu)
    window.browser.setHtml(EDITOR_HTML)

    splitter.addWidget(left_panel)
    splitter.addWidget(window.browser)
    splitter.setStretchFactor(1, 4)

    # --- 右侧属性面板 ---
    window.right_dock = QDockWidget("页面属性", window)
    window.right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
    window.right_dock_content = QWidget()
    window.right_dock_layout = QVBoxLayout(window.right_dock_content)

    window.lbl_theme_status = QLabel("<b>当前版式:</b> 无")
    window.lbl_theme_status.setWordWrap(True)
    window.lbl_theme_status.setStyleSheet("padding: 10px; background: #64b5f6; border: 1px solid #1976d2; border-radius: 5px; font-size: 14px;")

    window.lbl_bf_status = QLabel("<b>Better Footnotes:</b> 关闭")
    window.lbl_bf_status.setStyleSheet("padding: 10px; background: #e57373; border: 1px solid #d32f2f; border-radius: 5px; margin-top: 5px; font-size: 14px;")

    window.lbl_sidebar_status = QLabel("<b>Dark Sidebar:</b> 关闭")
    window.lbl_sidebar_status.setStyleSheet("padding: 10px; background: #95a5a6; border: 1px solid #7f8c8d; border-radius: 5px; margin-top: 5px; font-size: 14px; color: white;")

    window.right_dock_layout.addWidget(window.lbl_theme_status)
    window.right_dock_layout.addWidget(window.lbl_bf_status)
    window.right_dock_layout.addWidget(window.lbl_sidebar_status)
    window.right_dock_layout.addStretch()

    window.right_dock.setWidget(window.right_dock_content)
    window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, window.right_dock)