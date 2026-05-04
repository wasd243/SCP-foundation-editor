from ftml_client_py import process_footnotes as _process_footnotes


def process_footnotes(text: str, store) -> str:
    return _process_footnotes(text, store)
