from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class ClearConfirmDialog(QDialog):
    """一键清理确认对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("确认清理")
        self.setFixedSize(320, 130)
        layout = QVBoxLayout(self)

        label = QLabel("<b>确定要一键清理所有内容吗？</b>\n此操作将清空当前编辑的所有代码和版式设置。")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("确认清理")
        self.cancel_btn = QPushButton("取消")

        # 样式：大红按钮
        self.confirm_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; height: 30px;")
        self.cancel_btn.setStyleSheet("height: 30px;")

        self.confirm_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)