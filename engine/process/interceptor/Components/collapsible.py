from ftml_client_py import process_collapsible as _process_collapsible


def process_collapsible(text: str, store, inner_parser_cb, theme_type: str) -> str:
    return _process_collapsible(text, store, inner_parser_cb, theme_type)
