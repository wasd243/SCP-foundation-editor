from .utils import safe_get
import parse_node_py


def parse_acs(node, state, handle_parse_node_func):
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
