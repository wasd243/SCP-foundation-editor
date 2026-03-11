import re
from .utils import safe_get

def parse_acs(node, state, handle_parse_node_func):
    item = safe_get(node, '[data-field="item-number"]')
    clearance_raw = safe_get(node, '[data-field="clearance"]')
    
    clr_match = re.search(r'\d+', clearance_raw)
    clr = clr_match.group() if clr_match else "1"
    
    sec = safe_get(node, '[data-field="secondary"]').lower()
    if sec == "none": sec = ""
    cnt = '机密' if sec else safe_get(node, '[data-field="container"]').lower()
    dsr = safe_get(node, '[data-field="disruption"]').lower()
    rsk = safe_get(node, '[data-field="risk"]').lower()

    anim = ""
    if node.select_one('.acs-anim-checkbox') and node.select_one('.acs-anim-checkbox').has_attr('checked'):
        anim = "[[include :scp-wiki-cn:component:acs-animation]]\n"

    sec_line = ""
    if sec:
        sec_line = f"|secondary-class={sec}\n"
        sec_icon = safe_get(node, '[data-field="secondary-icon"]')
        if sec_icon: sec_line += f"|secondary-icon={sec_icon}\n"

    res = f"[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number={item}\n|clearance={clr}\n|container-class={cnt}\n{sec_line}|disruption-class={dsr}\n|risk-class={rsk}\n]]"
    
    if node.select_one('.acs-shiver-checkbox') and node.select_one('.acs-shiver-checkbox').has_attr('checked'):
        res = f'[[div class="Shivering-ACS"]]\n{res}\n[[/div]]'
    return f"\n{anim}{res}\n"
