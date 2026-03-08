from .utils import safe_get

def parse_user(node, state, handle_parse_node_func):
    return f"[[*user {safe_get(node, '.user-name')}]]"

def parse_user_adv(node, state, handle_parse_node_func):
    return f"[[*user {safe_get(node, '.user-name')}]]"
