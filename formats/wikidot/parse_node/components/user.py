# NOTE:
# This component is DOM-driven and tightly coupled with Python parsing logic.
# Do NOT migrate to Rust (PyO3) — would introduce unnecessary FFI overhead and complexity.

from .utils import safe_get

def parse_user(node, state, handle_parse_node_func):
    return f"[[*user {safe_get(node, '.user-name')}]]"

def parse_user_adv(node, state, handle_parse_node_func):
    return f"[[*user {safe_get(node, '.user-name')}]]"
