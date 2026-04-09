import os
import sys

# 优化日志，方便排查控制台错误
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3"
os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl


class EditorBridge(QObject):
    @pyqtSlot(str)
    def on_code_changed(self, content):
        print(f"🚀 [桥梁接收] 内容长度: {len(content)}")


class FoundationEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCP Foundation Editor")
        self.resize(1100, 800)

        self.browser = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = EditorBridge()

        self.channel.registerObject("py_bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        # 路径定位：main.py 同级有 assets 文件夹
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        self.load_editor()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.bridge.on_code_changed("--- 启动自检：Python 打印服务已在线 ---")

    def load_editor(self):
        html_path = os.path.join(self.base_dir, "code_view.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return

        # 核心关键：必须指定 baseUrl，否则 HTML 里的相对路径 (href="...") 无法加载
        # 注意末尾一定要带斜杠 "/"
        base_url = QUrl.fromLocalFile(self.base_dir + os.path.sep)
        self.browser.setHtml(html_content, base_url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FoundationEditor()
    window.show()
    sys.exit(app.exec())
