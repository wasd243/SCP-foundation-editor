from .utils import safe_get
import parse_node_py


def parse_aim(node, state, handle_parse_node_func):
    get_field = lambda d: safe_get(node, f'[data-field="{d}"]')
    blocks = node.get('data-blocks', '')

    return parse_node_py.parse_aim_component(
        blocks,
        get_field('xxxx'),
        get_field('lv'),
        get_field('cc'),
        get_field('dc'),
        get_field('site'),
        get_field('dir'),
        get_field('head'),
        get_field('mtf'),
    )
