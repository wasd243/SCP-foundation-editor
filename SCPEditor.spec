# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for SCP Foundation WYSIWYG Editor

block_cipher = None

# 收集所有需要随包打入的数据文件/目录
# 格式: (源路径, 打包后在 _MEIPASS 目录中的相对目标路径)
datas = [
    # HTML/CSS/JS 前端资源
    ('ui/css_styles', 'ui/css_styles'),
    # controllers/js 下的 JS 片段
    ('controllers/js', 'controllers/js'),
    # 引擎 Rust 扩展
    ('engine', 'engine'),
    # utils/templates 文本资源
    ('utils/templates', 'utils/templates'),
    # utils/js 资源
    ('utils/js', 'utils/js'),
    # 格式处理资源（如模板文件等）
    ('formats', 'formats'),
]

a = Analysis(
    ['Main.py'],
    pathex=['.'],
    binaries=[('engine/rust_engine/ftml_py/target/release/ftml_py.dll', 'engine/rust_engine/ftml_py')],
    datas=datas,
    hiddenimports=[
        # PyQt6 WebEngine 相关
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebChannel',
        # 项目内部模块（按需添加）
        'controllers',
        'controllers.MAIN_CONTROLLER',
        'controllers.menu_controller',
        'controllers.render_controller',
        'controllers.run_insert_js',
        'controllers.insert_basalt_div',
        'controllers.toolbar_controller',
        'controllers.initiate_save',
        'controllers.read_from_desktop',
        'controllers.open_editor.open_footnote_editor',
        'controllers.open_editor.open_audio_link_editor',
        'controllers.open_editor.open_license_link_editor',
        'engine.process.interceptor.MAIN_INTERCEPTOR',
        'formats.wikidot.wikidot_parser',
        'formats.wikidot.wikidot_exporter',
        'formats.wikidot.parse_node.parse_node',
        'ui.main_window_view',
        'ui.css_styles.html_template',
        'ui.widgets.CustomControlls',
        'ui.widgets.LinkDialog',
        'ui.widgets.SaveConfirmDialog',
        'ui.widgets.html_templates',
        'ui.toggle.toggle_config_panels',
        'ui.toggle.toggle_right_dock',
        'ui.toggle.on_basalt_toggled',
        'ui.toggle.on_shivering_toggled',
        'ui.toggle.on_bhl_toggled',
        'utils.resource_path',
        'utils.banner',
        'utils.logger',
        'utils.CSS_INJECTOR',
        'bs4',
        'ftml_py',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SCPEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,         # False = 不显示黑色终端窗口（GUI模式）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SCPEditor',
)
