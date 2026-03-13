"""
utils/resource_path.py

PyInstaller 打包兼容工具。

在开发环境下，返回相对于项目根目录的绝对路径。
在 PyInstaller 打包后（frozen），返回 _MEIPASS 临时解压目录的绝对路径。
"""
import sys
import os


def resource_path(*parts: str) -> str:
    """
    获取资源文件的绝对路径，兼容开发环境与 PyInstaller 打包后的环境。

    用法：
        resource_path('ui', 'css_styles', 'editor.html')
        resource_path('engine', 'rust_engine', 'ftml_py')

    在未打包状态，基准目录 = Main.py 所在目录（项目根）。
    在打包状态，   基准目录 = sys._MEIPASS（PyInstaller 临时解压目录）。
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        # 本文件在 utils/ 下，项目根是上一级
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)
