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