from ftml_client_py import process_tabview as _process_tabview


def process_tabview(text: str, store, inner_parser_cb, theme_type: str) -> str:
    return _process_tabview(text, store, inner_parser_cb, theme_type)
