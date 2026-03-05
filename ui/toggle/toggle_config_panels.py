def toggle_panels(ui):
    """
    处理组件选择器切换时，配置面板的显示与隐藏
    ui: SCPEditor 的实例 (即 Main 中的 self)
    """
    current = ui.comp_selector.currentText()
    
    # 控制玄武岩配置组的可见性
    ui.basalt_group.setVisible(current == "版式")
    
    # 控制 AIM 配置组的可见性
    ui.aim_group.setVisible(current == "AIM 高级信息方法论")