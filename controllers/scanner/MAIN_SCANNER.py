def scan_code(ui):
    """扫描源代码内容"""
    import json

    if getattr(ui, 'source_editor_window', None) is None:
        return
    if getattr(ui, 'source_display', None) is None:
        print("⚠️ 警告：ui.source_display 不存在")
        return

    code_content = ui.source_display.toPlainText()
