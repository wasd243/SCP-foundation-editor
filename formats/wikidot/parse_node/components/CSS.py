from .utils import safe_get

def parse_css_module(node, state, handle_parse_node_func):
    css_code = safe_get(node, '.css-content', 'text').strip()
    return f"\n[[module CSS]]\n{css_code}\n[[/module]]\n"
