import re

COLOR_MAP = {
    'safe': '#27ae60',
    'euclid': '#f1c40f',
    'keter': '#c0392b',
    'neutralized': '#7f8c8d', 
    'pending': '#bdc3c7',     
    'explained': '#95a5a6',   
    'esoteric': '#595959',
    '机密': '#595959' 
}

ACS_ICON_MAP = {
    'apollyon': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/apollyon-icon.svg',
    'archon': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/archon-icon.svg',
    'hiemal': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/hiemal-icon.svg',
    'tiamat': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/tiamat-icon.svg',
    'ticonderoga': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/ticonderoga-icon.svg',
    'thaumiel': 'https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/thaumiel-icon.svg'
}

def process_acs(text: str, store) -> str:
    """
    处理 ACS 异常分级组件
    """
    processed_text = text
    
    # 注入夜琉璃 (Shivering) 标记
    processed_text = re.sub(r'\[\[div class="Shivering-ACS"\]\]\s*(\[\[include :scp-wiki-cn:component:anomaly-class-bar-source.*?\]\])\s*\[\[/div\]\]', r'\1 |data-shivering=true', processed_text, flags=re.DOTALL)

    def acs_replacer(match):
        source = match.group(0)
        def get_arg(name):
            m = re.search(fr'(?:\||\s){name}=([^\|\n\]]+)', source)
            return m.group(1).strip() if m else ""
        
        item = get_arg('item-number')
        clr_match = re.search(r'\d+', get_arg('clearance'))
        clr = clr_match.group() if clr_match else '1'
        cnt = get_arg('container-class').lower()
        sec = get_arg('secondary-class').lower()
        sec_icon = get_arg('secondary-icon')
        dsr = get_arg('disruption-class')
        rsk = get_arg('risk-class')

        # === 核心改进补充：处理存在次要分级时的行为 ===
        if sec and sec != 'none':
            cnt = '机密'  # 在中文站中，有次要分级自动把主项目等级折叠为“机密” (Esoteric)
            if not sec_icon and sec in ACS_ICON_MAP:
                sec_icon = ACS_ICON_MAP[sec]  # 自动填充 SVG 链接
        # ==========================================
        
        color = COLOR_MAP.get(cnt, '#595959')
        anim_checked = 'checked' if 'component:acs-animation' in processed_text else ''
        is_shiver = get_arg('data-shivering') == 'true'
        shiver_checked = 'checked' if is_shiver else ''

        html = f'''<div class="scp-component acs-box" data-type="acs" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-clearance="{clr}" data-container="{cnt}" data-secondary="{sec or 'none'}" data-disruption="{dsr}" data-risk="{rsk}" data-shivering="{str(is_shiver).lower()}" style="--acs-color: {color};" contenteditable="false"><div class="acs-header-row" contenteditable="false"><div class="acs-title">SCP-CN 异常分级栏</div><div class="acs-toggles"><div class="acs-anim-toggle"><span>动画:</span><label class="switch"><input type="checkbox" class="acs-anim-checkbox" {anim_checked}><span class="slider"></span></label></div><div class="acs-shiver-toggle"><span>夜琉璃适配:</span><label class="switch"><input type="checkbox" class="acs-shiver-checkbox" {shiver_checked}><span class="slider"></span></label></div></div><div class="acs-item-num" contenteditable="true" data-field="item-number">{item}</div></div><div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 10px;"><div><small style="color:#888; font-size:9px; text-transform:uppercase;">许可等级</small><br><b data-field="clearance" contenteditable="true">{clr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">项目等级</small><br><b data-field="container" style="color:var(--acs-color)" contenteditable="true">{cnt}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">次要等级</small><br><b data-field="secondary" contenteditable="true">{sec or "none"}</b><div style="font-size:0.8em; border-top:1px solid #ccc; margin-top:2px;">Icon: <span data-field="secondary-icon" contenteditable="true" style="min-width:20px; display:inline-block; word-break: break-all;">{sec_icon}</span></div></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">扰动等级</small><br><b data-field="disruption" contenteditable="true">{dsr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">风险等级</small><br><b data-field="risk" contenteditable="true">{rsk}</b></div></div></div>'''
        return store.register_html(source, "acs", html)
        
    processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:anomaly-class-bar-source.*?\]\]', acs_replacer, processed_text, flags=re.DOTALL)
    processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:acs-animation\]\]', '', processed_text)

    return processed_text
