try:
    import exporter_py
except ImportError as exc:
    raise ImportError("exporter_py is required for wikidot export") from exc


def export_html_to_wikidot(html: str, snapshot: dict) -> str:
    return exporter_py.export_html_to_wikidot(html, snapshot)
