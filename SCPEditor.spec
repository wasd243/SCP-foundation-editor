# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = collect_submodules('PyQt6.QtWebEngine')

datas = [
    ('ui/css_styles', 'ui/css_styles'),
    ('controllers/js', 'controllers/js'),
    ('utils/templates', 'utils/templates'),
    ('utils/js', 'utils/js'),
    ('formats', 'formats'),
]

binaries = [
    ('engine/rust_engine/ftml_py/target/release/ftml_py.dll', '.')
]

a = Analysis(
    ['Main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + ['bs4', 'ftml_py'],
    excludes=['tkinter', 'matplotlib'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SCPEditor',
    console=False,
    upx=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SCPEditor',
)
