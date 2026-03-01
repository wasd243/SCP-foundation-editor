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
import json
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtWebEngineCore import QWebEnginePage

class PlainPasteTextEdit(QTextEdit):
    """纯文本粘贴代码视窗，防止粘贴时带有外部富文本格式"""
    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)


class CustomWebPage(QWebEnginePage):
    """Custom WebPage 拦截导航请求 (用于脚注和链接编辑)"""
    def __init__(self, parent=None, editor=None):
        super().__init__(parent)
        self.editor = editor  # 这里的 editor 实际上就是传进来的主窗口 (SCPEditor)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # 拦截 "edit-footnote://" 协议
        if url.scheme() == "edit-footnote":
            try:
                u_str = url.toString()
                idx_str = u_str.replace("edit-footnote://", "")
                if idx_str.isdigit() and self.editor:
                    self.editor.open_footnote_editor(int(idx_str))
            except Exception as e:
                print(f"Footnote navigation error: {e}")
            return False
            
        # 拦截 "edit-license-link://" 协议
        if url.scheme() == "edit-license-link":
            try:
                u_str = url.toString()
                elem_id = u_str.replace("edit-license-link://", "")
                if elem_id and self.editor:
                    self.editor.open_license_link_editor(elem_id)
            except Exception as e:
                print(f"License link navigation error: {e}")
            return False

        # 拦截 "edit-audio-link://" 协议
        if url.scheme() == "edit-audio-link":
            try:
                u_str = url.toString()
                elem_id = u_str.replace("edit-audio-link://", "")
                if elem_id and self.editor:
                    self.editor.open_audio_link_editor(elem_id)
            except Exception as e:
                print(f"Audio link navigation error: {e}")
            return False

        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # 拦截 JS console 日志进行前后端状态同步 (工具栏按钮状态高亮)
        if message.startswith("SYNC_STATE:"):
            try:
                state_json = message.replace("SYNC_STATE:", "", 1)
                if state_json and self.editor:
                    state = json.loads(state_json)
                    self.editor.sync_toolbar(state)
            except Exception as e:
                print(f"[IPC Error] sync-toolbar json decode failed: {e}")
            return
            
        # 捕获其他 Javascript console.logs 并打印到 Python 终端
        print(f"[JS Console] Line {lineNumber}: {message}")