import json
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtWebEngineCore import QWebEnginePage

class PlainPasteTextEdit(QTextEdit):
    """纯文本粘贴代码视窗，防止粘贴时带有外部富文本格式"""
    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)


class CustomWebPage(QWebEnginePage):
    """Custom WebPage 拦截导航请求 (用于脚注和链接编辑)"""
    def __init__(self, parent=None, editor=None):
        super().__init__(parent)
        self.editor = editor  # 这里的 editor 实际上就是传进来的主窗口 (SCPEditor)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # 拦截 "edit-footnote://" 协议
        if url.scheme() == "edit-footnote":
            try:
                u_str = url.toString()
                idx_str = u_str.replace("edit-footnote://", "")
                if idx_str.isdigit() and self.editor:
                    self.editor.open_footnote_editor(int(idx_str))
            except Exception as e:
                print(f"Footnote navigation error: {e}")
            return False
            
        # 拦截 "edit-license-link://" 协议
        if url.scheme() == "edit-license-link":
            try:
                u_str = url.toString()
                elem_id = u_str.replace("edit-license-link://", "")
                if elem_id and self.editor:
                    self.editor.open_license_link_editor(elem_id)
            except Exception as e:
                print(f"License link navigation error: {e}")
            return False

        # 拦截 "edit-audio-link://" 协议
        if url.scheme() == "edit-audio-link":
            try:
                u_str = url.toString()
                elem_id = u_str.replace("edit-audio-link://", "")
                if elem_id and self.editor:
                    self.editor.open_audio_link_editor(elem_id)
            except Exception as e:
                print(f"Audio link navigation error: {e}")
            return False

        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # 拦截 JS console 日志进行前后端状态同步 (工具栏按钮状态高亮)
        if message.startswith("SYNC_STATE:"):
            try:
                state_json = message.replace("SYNC_STATE:", "", 1)
                if state_json and self.editor:
                    state = json.loads(state_json)
                    self.editor.sync_toolbar(state)
            except Exception as e:
                print(f"[IPC Error] sync-toolbar json decode failed: {e}")
            return
            
        # 捕获其他 Javascript console.logs 并打印到 Python 终端
        print(f"[JS Console] Line {lineNumber}: {message}")