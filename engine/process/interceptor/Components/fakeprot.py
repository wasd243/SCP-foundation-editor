from ftml_client_py import process_fakeprot as _process_fakeprot


def process_fakeprot(text: str, store, inner_parser_cb, theme_type: str) -> str:
    return _process_fakeprot(text, store, inner_parser_cb, theme_type)
