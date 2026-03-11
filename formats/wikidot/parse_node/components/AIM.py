from .utils import safe_get

def parse_aim(node, state, handle_parse_node_func):
    f = lambda d: safe_get(node, f'[data-field="{d}"]')
    blocks = node.get('data-blocks', '')
    code = "[[include :scp-wiki-cn:component:advanced-information-methodology\n"
    if blocks: code += f"|blocks={blocks}\n"
    code += "|lang=CN\n"
    if blocks != '!': code += f"|XXXX={f('xxxx')}\n|lv={f('lv')}\n|cc={f('cc')}\n|dc={f('dc')}\n"
    if blocks != '-': code += f"|site={f('site')}\n|dir={f('dir')}\n|head={f('head')}\n|mtf={f('mtf')}\n"
    code += "]]\n"
    return code
