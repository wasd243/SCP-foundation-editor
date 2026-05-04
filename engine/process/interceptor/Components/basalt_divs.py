from ftml_client_py import process_basalt_divs as _process_basalt_divs

def process_basalt_divs(text: str, store, inner_parser_cb, theme_type: str) -> str:
    return _process_basalt_divs(text, store, inner_parser_cb, theme_type)
