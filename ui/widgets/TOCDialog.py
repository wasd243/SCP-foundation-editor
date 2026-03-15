from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel
)

class TOCDialog(QDialog):
    """添加标题到目录对话框"""
    def __init__(self, parent=None, default_name="", default_anchor=""):
        super().__init__(parent)
        self.setWindowTitle("添加标题到目录")
        self.setMinimumWidth(350)
        
        self.layout = QVBoxLayout(self)
        
        self.form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setText(default_name)
        self.name_input.setPlaceholderText("在目录中显示的名称")
        
        self.anchor_input = QLineEdit()
        self.anchor_input.setText(default_anchor)
        self.anchor_input.setPlaceholderText("例如: my-heading-link")
        
        self.form.addRow("目录名称:", self.name_input)
        self.form.addRow("目录代码名:", self.anchor_input)
        
        self.layout.addLayout(self.form)
        
        self.tip = QLabel("<font color='gray' size='2'>提示: 目录代码名将作为 [[# 代码名]] 插入到标题中。</font>")
        self.layout.addWidget(self.tip)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return self.name_input.text().strip(), self.anchor_input.text().strip()
