import os
import sys

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3"
os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl, pyqtSignal  # ← 新增 pyqtSignal


class EditorBridge(QObject):
    # ✅ 新增：内容变更信号，供外部（toolbar_controller）订阅
    content_changed = pyqtSignal(str)

    @pyqtSlot(str)
    def on_code_changed(self, content):
        print(f"🚀 [桥梁接收] 内容长度: {len(content)}")
        # ✅ 新增：发射信号，把内容广播出去
        self.content_changed.emit(content)


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

        base_url = QUrl.fromLocalFile(self.base_dir + os.path.sep)
        self.browser.setHtml(html_content, base_url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FoundationEditor()
    window.show()
    sys.exit(app.exec())
