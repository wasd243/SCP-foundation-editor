from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QCheckBox, QDialogButtonBox, QVBoxLayout
)

class LinkDialog(QDialog):
    """简单的插入链接对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插入链接")
        
        # 建议这里使用 QFormLayout，因为它最适合用来做“表单”布局（左边文字，右边输入框）
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