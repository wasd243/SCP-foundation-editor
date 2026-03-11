# ============================================================
# SCP Foundation WYSIWYG Editor
#
# Copyright (C) 2026 Zichen Wang (wasd243)
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, version 3.
#
# This program is distributed WITHOUT ANY WARRANTY.
#
# https://www.gnu.org/licenses/agpl-3.0.html
# ============================================================

#  特别说明：本项目涉及的 SCP 基金会相关组件及版式遵循 CC BY-SA 3.0 协议。
#  版权信息声明：
#  本项目涉及的 SCP 基金会相关组件及版式遵循 CC BY-SA 3.0 协议。


#  ACS 作者：
#  异常分类系统由 Woedenaz 编撰，同时感谢以下各位提供的大力帮助：
#  The Great Hippo 
#  Rounderhouse
#  djkaktus
#  Yossipossi
#  Captain Kirby
#  CadaverCommander
#  Uncle Nicolini
#  aismallard
#  Jade Skylar
#  Lt Flops
#  Sterbai
#  链接：https://scp-wiki-cn.wikidot.com/anomaly-classification-system-guide 


#  AIM 作者：Dr Moned；译者：hoah2333hoah2333
#  链接：https://scp-wiki.wikidot.com/component:advanced-information-methodology


#  玄武岩版式 作者：Liryn 和 Placeholder McD
#  链接：https://scp-wiki.wikidot.com/theme:basalt


#  更好的脚注 作者：EstrellaYoshte
#  链接：https://scp-wiki.wikidot.com/component:betterfootnotes

#  ACS动画 作者：EstrellaYoshte
#  链接：https://scp-wiki.wikidot.com/component:acs-animation


#  夜琉璃版式 作者：Flea_ZER0 
#  链接：https://scp-wiki-cn.wikidot.com/theme:shivering-night


#  黑色标记笔版式 这个项目由：Woedenaz 和 Croquembouche 负责
#  链接：https://scp-wiki.wikidot.com/theme:black-marker

#  办公室子版式 作者：Woedenaz
#  链接：https://scp-wiki.wikidot.com/theme:scp-offices-theme


#  CSS 样式表（CSS和div模块快捷代码）由：aismallard Jerden Lt Flops EstrellaYoshte Deadly Bread Rounderhouse stormbreath 
#  Croquembouche Calibold 和 Dr Hormress 汇总，
#  链接：https://scp-wiki.wikidot.com/scp-style-resource
#  中文链接：https://scp-wiki-cn.wikidot.com/scp-style-resource 
import sys
import os
from PyQt6.QtWidgets import QApplication

# 从 controllers 包中导入业务主类
# 确保你已经将原来的 SCPEditor 类移动到了 controllers/main_controller.py
from controllers.MAIN_CONTROLLER import SCPEditor
from utils.banner import print_startup_banner
from utils.logger import *
# 处理终端报错问题
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3"

print_startup_banner()
log("INIT", "Application starting")
log("QT", "Initializing PyQt6")
log("ENGINE", "Loading FTML renderer")
log_ok("Editor ready")

if __name__ == "__main__":
    # 初始化应用
    app = QApplication(sys.argv)
    
    # 实例化主控制器窗口
    window = SCPEditor()
    window.show()
    
    # 进入程序主循环
    sys.exit(app.exec())
