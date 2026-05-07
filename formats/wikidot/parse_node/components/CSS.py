# NOTE:
# This component is DOM-driven and tightly coupled with Python parsing logic.
# Do NOT migrate to Rust (PyO3) — would introduce unnecessary FFI overhead and complexity.

from .utils import safe_get

def parse_css_module(node, state, handle_parse_node_func):
    css_code = safe_get(node, '.css-content', 'text').strip()
    return f"\n[[module CSS]]\n{css_code}\n[[/module]]\n"
