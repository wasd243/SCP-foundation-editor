from ftml_client_py import process_toc as _process_toc


def process_toc(text: str, store, inner_parser_cb, theme_type: str) -> str:
    return _process_toc(text, store, inner_parser_cb, theme_type)
