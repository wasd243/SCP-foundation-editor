from .utils import safe_get

def parse_image_block(node, state, handle_parse_node_func):
    name = safe_get(node, '[data-field="name"]')
    caption = safe_get(node, '[data-field="caption"]')
    align = node.get('data-align', 'right')
    return f"\n[[include component:image-block name={name}\n|caption={caption}\n|align={align}]]\n"

def parse_image_block_adv(node, state, handle_parse_node_func):
    name = safe_get(node, '[data-field="name"]')
    caption = safe_get(node, '[data-field="caption"]')
    width = safe_get(node, '[data-field="width"]')
    height = safe_get(node, '[data-field="height"]')
    align = node.get('data-align', 'right')

    res = f"\n[[include component:image-block\n|name={name}\n|caption={caption}"
    if width:
        width_val = width.lower().strip()
        if width_val and not (width_val.endswith('px') or width_val.endswith('%')): width_val += "px"
        res += f"\n|width={width_val}"
    if height:
        height_val = height.lower().strip()
        if height_val and not (height_val.endswith('px') or height_val.endswith('%')): height_val += "px"
        res += f"\n|height={height_val}"
    res += f"\n|align={align}]]\n"
    return res
