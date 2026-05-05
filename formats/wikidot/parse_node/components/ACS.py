import re
from .utils import safe_get

try:
    import parse_node_py
    HAS_PARSE_NODE_RUST = True
except ImportError:
    HAS_PARSE_NODE_RUST = False


def _parse_acs_python_fallback(node):
    item = safe_get(node, '[data-field="item-number"]')
    clearance_raw = safe_get(node, '[data-field="clearance"]')

    clr_match = re.search(r'\d+', clearance_raw)
    clr = clr_match.group() if clr_match else "1"

    sec = safe_get(node, '[data-field="secondary"]').lower()
    if sec == "none":
        sec = ""
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
        if sec_icon:
            sec_line += f"|secondary-icon={sec_icon}\n"

    res = f"[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number={item}\n|clearance={clr}\n|container-class={cnt}\n{sec_line}|disruption-class={dsr}\n|risk-class={rsk}\n]]"

    if node.select_one('.acs-shiver-checkbox') and node.select_one('.acs-shiver-checkbox').has_attr('checked'):
        res = f'[[div class="Shivering-ACS"]]\n{res}\n[[/div]]'
    return f"\n{anim}{res}\n"

def parse_acs(node, state, handle_parse_node_func):
    if not HAS_PARSE_NODE_RUST:
        return _parse_acs_python_fallback(node)

    item = safe_get(node, '[data-field="item-number"]')
    clearance_raw = safe_get(node, '[data-field="clearance"]')
    secondary_raw = safe_get(node, '[data-field="secondary"]')
    container_raw = safe_get(node, '[data-field="container"]')
    secondary_icon_raw = safe_get(node, '[data-field="secondary-icon"]')
    disruption_raw = safe_get(node, '[data-field="disruption"]')
    risk_raw = safe_get(node, '[data-field="risk"]')

    anim_checked = (
        node.select_one('.acs-anim-checkbox')
        and node.select_one('.acs-anim-checkbox').has_attr('checked')
    )
    shiver_checked = (
        node.select_one('.acs-shiver-checkbox')
        and node.select_one('.acs-shiver-checkbox').has_attr('checked')
    )

    return parse_node_py.parse_acs_component(
        item,
        clearance_raw,
        secondary_raw,
        container_raw,
        secondary_icon_raw,
        disruption_raw,
        risk_raw,
        bool(anim_checked),
        bool(shiver_checked),
    )
