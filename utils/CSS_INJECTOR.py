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
import os

# 获取当前文件所在的目录 (即 utils 目录)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def _run_injection(page, x, y, filename):
    """通用的 JS 模板读取与执行核心"""
    js_path = os.path.join(CURRENT_DIR, 'js', filename)
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()
        
        # 只替换坐标占位符，安全又高效
        final_js = js_template.replace('__POS_X__', str(x)).replace('__POS_Y__', str(y))
        page.runJavaScript(final_js)
    except Exception as e:
        print(f"读取组件注入脚本失败 ({js_path}): {e}")

# =========================================================================
# 以下所有的注入动作，全部变成了极其清爽的单行转发！
# 对应 utils/js/ 目录下的各自 js 模板
# =========================================================================
def inject_terminal_shortcut(page, x, y): _run_injection(page, x, y, 'inject_terminal_shortcut.js')
def inject_terminal_001(page, x, y): _run_injection(page, x, y, 'inject_terminal_001.js')
def inject_raisa_notice(page, x, y): _run_injection(page, x, y, 'inject_raisa_notice.js')
def inject_class_warning(page, x, y): _run_injection(page, x, y, 'inject_class_warning.js')
def inject_foundation_background(page, x, y): _run_injection(page, x, y, 'inject_foundation_bg.js')
def inject_o5_command(page, x, y): _run_injection(page, x, y, 'inject_o5_command.js')
def inject_video_record(page, x, y): _run_injection(page, x, y, 'inject_video_record.js')
def inject_video_record2(page, x, y): _run_injection(page, x, y, 'inject_video_record2.js')
def inject_page_note(page, x, y): _run_injection(page, x, y, 'inject_page_note.js')
def inject_email_template(page, x, y): _run_injection(page, x, y, 'inject_email_template.js')
def inject_login_logout(page, x, y): _run_injection(page, x, y, 'inject_login_logout.js')