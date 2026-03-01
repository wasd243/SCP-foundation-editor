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
import html

def get_aim_template(blocks_mode="full"):
    """
    根据模式返回 AIM 模块的 HTML 模板
    blocks_mode: 'full' (完整), '-' (仅上半), '!' (仅下半)
    """
    blocks_attr = ""
    row_style_top = ""
    row_style_bottom = ""
    footer_text = "AIM 完整版头"

    if blocks_mode == "-":
        blocks_attr = 'data-blocks="-"'
        row_style_bottom = 'style="display:none;"'
        footer_text = "仅上半部分的 AIM 示例"
    elif blocks_mode == "!":
        blocks_attr = 'data-blocks="!"'
        row_style_top = 'style="display:none;"'
        footer_text = "仅下半部分的 AIM 示例"

    return f'''<div class="scp-component aim-box" data-type="aim" {blocks_attr} contenteditable="false"><table class="aim-table"><tr {row_style_top}><td colspan="2"><div class="aim-label">项目编号</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">SCP-XXXX</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">等级 / 公开</div><div class="aim-value" data-field="lv" contenteditable="true">等级-01/公开</div></td></tr><tr {row_style_top}><td colspan="2"><div class="aim-label">收容等级</div><div class="aim-value" data-field="cc" contenteditable="true">THAUMIEL</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">扰动等级</div><div class="aim-value" data-field="dc" contenteditable="true">DARK</div></td></tr><tr {row_style_bottom} style="text-align: center; background: #fafafa;"><td><div class="aim-label">负责站点</div><div class="aim-value" data-field="site" contenteditable="true">Site-0</div></td><td><div class="aim-label">站点主管</div><div class="aim-value" data-field="dir" contenteditable="true">Dr 主管</div></td><td><div class="aim-label">首席研究员</div><div class="aim-value" data-field="head" contenteditable="true">Dr 博士</div></td><td><div class="aim-label">指派特遣队</div><div class="aim-value" data-field="mtf" contenteditable="true">Alpha-1</div></td></tr></table><div class="aim-footer">{footer_text}</div></div><p><br></p>'''

# 静态组件模板字典
COMPONENT_TEMPLATES = {
    "图片块 (Image Block)": '''<div class="scp-component image-block-box" data-type="image-block-adv" data-align="right" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'center')" onmousedown="event.stopPropagation();">置中</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div><div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div style="display:flex; align-items:center;"><b style="flex-shrink:0;">源: &nbsp;</b><span data-field="name" style="display:none;">link/to/image.jpg</span><span class="img-link-label" onclick="editImgLink(this)" onmousedown="event.stopPropagation();" style="color:blue; text-decoration:underline; cursor:pointer;">链接</span></div><div style="display:flex; justify-content:space-between; align-items:baseline;"><span><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span></span> <span><b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span></span></div></div></div><div class="image-block-content"><img src="" class="img-preview" style="max-width:100%; display:none; margin:0 auto 5px auto;"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">在此输入图片描述</span></div></div>''',
    
    "高级图片块 (Advanced Image)": '''<div class="scp-component image-block-box" data-type="image-block-adv" data-align="right" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'center')" onmousedown="event.stopPropagation();">置中</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div><div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div style="display:flex; align-items:center;"><b style="flex-shrink:0;">源: &nbsp;</b><span data-field="name" style="display:none;">link/to/image.jpg</span><span class="img-link-label" onclick="editImgLink(this)" onmousedown="event.stopPropagation();" style="color:blue; text-decoration:underline; cursor:pointer;">链接</span></div><div style="display:flex; justify-content:space-between; align-items:baseline;"><span><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span></span> <span><b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;"></span></span></div></div></div><div class="image-block-content"><img src="" class="img-preview" style="max-width:100%; display:none; margin:0 auto 5px auto;"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">在此输入图片描述</span></div></div>''',

    "Tab View (选项卡)": '''<div class="scp-component tabview-box" data-type="tabview" contenteditable="false"><div class="tab-header"><span class="tab-btn active" onclick="selectTab(this)" contenteditable="true">Tab 1</span><span class="tab-btn" onclick="selectTab(this)" contenteditable="true">Tab 2</span><span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents"><div class="tab-item active" contenteditable="true"><p>Tab 1 Content...</p></div><div class="tab-item" contenteditable="true"><p>Tab 2 Content...</p></div></div></div><p><br></p>''',

    "用户标签 (User)": '''<span class="scp-component user-tag" data-type="user" contenteditable="false"><div class="user-icon"></div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">User Name</span></span>''',

    "高级用户信息 (Advanced User)": '''<span class="scp-component user-tag" data-type="user-adv" contenteditable="false"><div class="user-icon" style="background:gold; text-align:center; line-height:12px; font-size:10px; color:#fff;">★</div><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">User Name</span></span>''',

    "ACS 分级系统": '''<div class="scp-component acs-box" data-type="acs" data-clearance="2" data-container="euclid" data-secondary="none" data-disruption="vlam" data-risk="notice" data-shivering="false" style="--acs-color: #f1c40f;" contenteditable="false"><div class="acs-header-row" contenteditable="false"><div class="acs-title">SCP-CN 异常分级栏</div><div class="acs-toggles"><div class="acs-anim-toggle"><span>动画:</span><label class="switch"><input type="checkbox" class="acs-anim-checkbox"><span class="slider"></span></label></div><div class="acs-shiver-toggle"><span>夜琉璃适配:</span><label class="switch"><input type="checkbox" class="acs-shiver-checkbox"><span class="slider"></span></label></div></div><div class="acs-item-num" contenteditable="true" data-field="item-number">SCP-CN-XXXX</div></div><div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 10px;"><div><small style="color:#888; font-size:9px; text-transform:uppercase;">许可等级</small><br><b data-field="clearance" contenteditable="true">2级</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">项目等级</small><br><b data-field="container" style="color:var(--acs-color)" contenteditable="true">Euclid</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">次要等级</small><br><b data-field="secondary" contenteditable="true">none</b><div style="font-size:0.8em; border-top:1px solid #ccc; margin-top:2px;">Icon: <span data-field="secondary-icon" contenteditable="true" style="min-width:20px; display:inline-block"></span></div></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">扰动等级</small><br><b data-field="disruption" contenteditable="true">Vlam</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">风险等级</small><br><b data-field="risk" contenteditable="true">Notice</b></div></div></div><p><br></p>''',

    "折叠块 (Collapsible)": '''<div class="scp-component collapsible-box open" data-type="collapsible" contenteditable="false"><div class="collapsible-header"><span><span class="title-label">显示标题:</span> <span class="title-input" data-field="show" contenteditable="true">+ 打开折叠内容</span></span><span><span class="title-label">隐藏标题:</span> <span class="title-input" data-field="hide" contenteditable="true">- 关闭折叠内容</span></span></div><div class="collapsible-content-area" contenteditable="true"><p>在这里输入折叠内的内容...</p></div></div><p><br></p>''',

    "DIV 模块": '''<div class="scp-component div-box" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="true">DIV: class="example"</div><div class="div-content" contenteditable="true"><p>输入正文...</p></div></div><p><br></p>''',

    "CSS 模块": '''<div class="scp-component css-box" data-type="css-module" contenteditable="false"><div class="css-header">CSS Module (Valid CSS Only)</div><div class="css-content" contenteditable="true">/* Input CSS here */</div><div class="css-hint">被css影响的代码紧跟css模块下面</div></div><p><br></p>'''
}