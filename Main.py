#  Copyright (C) 2026  wasd243
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
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

# 处理终端报错问题
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3"

if __name__ == "__main__":
    # 在启动 GUI 之前，在终端打印 GPL 法律通告及版权信息
    print("-" * 60)
    print("SCP-foundation-editor  Copyright (C) 2026  wasd243")
    print("This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.")
    print("This is free software, and you are welcome to redistribute it")
    print("under certain conditions; type `show c' for details.")
    print("-" * 60)
    
    print('To View the whole document, please visit https://github.com/wasd243/SCP-foundation-editor/')
    print('For further information of this program, you can see at Main.py')
    print('-' * 60)
    # 初始化应用
    app = QApplication(sys.argv)
    
    # 实例化主控制器窗口
    window = SCPEditor()
    window.show()
    
    # 进入程序主循环
    sys.exit(app.exec())