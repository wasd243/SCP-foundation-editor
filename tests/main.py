import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl

# 优化日志，方便排查控制台错误
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3"

class EditorBridge(QObject):
    @pyqtSlot(str)
    def on_code_changed(self, content):
        print(f"[Python] 代码更新: {len(content)} 字符")

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

        # 路径定位：假设 main.py 同级有 assets 文件夹
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        self.load_editor()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_editor(self):
        html_path = os.path.join(self.assets_dir, "index.html")
        
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return

        # 核心关键：必须指定 baseUrl，否则 HTML 里的相对路径 (href="...") 无法加载
        # 注意末尾一定要带斜杠 "/"
        base_url = QUrl.fromLocalFile(self.assets_dir + os.path.sep)
        self.browser.setHtml(html_content, base_url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FoundationEditor()
    window.show()
    sys.exit(app.exec())