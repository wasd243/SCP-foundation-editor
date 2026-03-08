from .utils import safe_get

def parse_html5player(node, state, handle_parse_node_func):
    url = safe_get(node, '.html5player-url', 'text')
    return f"[[include :snippets:html5player\n|type=audio\n|url={url}]]\n"
