import re

def process_aim(text: str, store) -> str:
    """
    处理 AIM (Advanced Information Methodology) 组件
    解析 [[include :scp-wiki-cn:component:advanced-information-methodology]] 语法
    并利用 CSS 表格直接渲染出可编辑的对应页面属性。
    """
    processed_text = text

    def aim_replacer(match):
        source = match.group(0)
        def get_arg(name):
            m = re.search(fr'(?:\||\s+)\s*{name}\s*=\s*([^\|\n\]]+)', source, re.IGNORECASE)
            return m.group(1).strip() if m else "???"
        
        blocks_arg = get_arg('blocks')
        row_style_top = 'display:none;' if blocks_arg == '!' else ''
        row_style_bottom = 'display:none;' if blocks_arg == '-' else ''
        
        html = f'''<div class="scp-component aim-box" data-type="aim" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-blocks="{blocks_arg}" contenteditable="false"><table class="aim-table"><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">项目编号</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">{get_arg('XXXX')}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">等级 / 公开</div><div class="aim-value" data-field="lv" contenteditable="true">{get_arg('lv')}</div></td></tr><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">收容等级</div><div class="aim-value" data-field="cc" contenteditable="true">{get_arg('cc')}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">扰动等级</div><div class="aim-value" data-field="dc" contenteditable="true">{get_arg('dc')}</div></td></tr><tr style="{row_style_bottom} text-align: center; background: #fafafa;"><td><div class="aim-label">负责站点</div><div class="aim-value" data-field="site" contenteditable="true">{get_arg('site')}</div></td><td><div class="aim-label">站点主管</div><div class="aim-value" data-field="dir" contenteditable="true">{get_arg('dir')}</div></td><td><div class="aim-label">首席研究员</div><div class="aim-value" data-field="head" contenteditable="true">{get_arg('head')}</div></td><td><div class="aim-label">指派特遣队</div><div class="aim-value" data-field="mtf" contenteditable="true">{get_arg('mtf')}</div></td></tr></table><div class="aim-footer">AIM Module</div></div>'''
        
        return store.register_html(source, "aim", html)

    processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:advanced-information-methodology.*?\]\]', aim_replacer, processed_text, flags=re.DOTALL)
    
    return processed_text
