from .utils import safe_get

def parse_collapsible(node, state, handle_parse_node_func):
    show_t = safe_get(node, '[data-field="show"]')
    hide_t = safe_get(node, '[data-field="hide"]')
    content_area = node.select_one('.collapsible-content-area') or node.select_one('.collapsible-content') or node
    inner = "".join(handle_parse_node_func(c, state) for c in content_area.contents) if content_area else ""
    return f'\n[[collapsible show="{show_t}" hide="{hide_t}"]]\n{inner.strip()}\n[[/collapsible]]\n'
