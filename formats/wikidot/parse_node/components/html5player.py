# NOTE:
# This component is DOM-driven and tightly coupled with Python parsing logic.
# Do NOT migrate to Rust (PyO3) — would introduce unnecessary FFI overhead and complexity.

from .utils import safe_get

def parse_html5player(node, state, handle_parse_node_func):
    url = safe_get(node, '.html5player-url', 'text')
    return f"[[include :snippets:html5player\n|type=audio\n|url={url}]]\n"
