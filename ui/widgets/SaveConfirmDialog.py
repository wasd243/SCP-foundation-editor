from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class SaveConfirmDialog(QDialog):
    """保存确认对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("保存文件")
        self.setFixedSize(300, 120)
        layout = QVBoxLayout(self)

        label = QLabel("确认保存当前文档？\n(将以 .txt 格式保存至桌面)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("确认保存")
        self.cancel_btn = QPushButton("取消")

        # 样式微调
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)