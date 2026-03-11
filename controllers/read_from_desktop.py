from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QTabWidget
)
import os
def read_from_desktop(read_desk):
    """Prompt user for a .txt file on the desktop, read it, and reverse-parse it to the editor"""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path, _ = QFileDialog.getOpenFileName(
        read_desk,
        "选择要读取的 .txt 文件",
        desktop,
        "Text Files (*.txt);;All Files (*)"
    )
        
    if not file_path:
        return 
        
    if not file_path.lower().endswith(".txt"):
        QMessageBox.warning(read_desk, "读取失败", "请选择 .txt 后缀的文本文件！")
        return
            
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        read_desk.source_display.setPlainText(content)
        read_desk.render_to_editor()
        read_desk.centralWidget().findChild(QTabWidget).setCurrentIndex(0)
        QMessageBox.information(read_desk, "读取成功", f"文件内容已成功加载并渲染：\n{file_path}\n（注：复杂代码结构可能无法完全还原在UI中）")
    except Exception as e:
        QMessageBox.warning(read_desk, "读取失败", f"读取文件时发生错误：{str(e)}")