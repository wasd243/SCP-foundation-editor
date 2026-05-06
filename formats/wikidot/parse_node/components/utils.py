# NOTE:
# This component is DOM-driven and tightly coupled with Python parsing logic.
# Do NOT migrate to Rust (PyO3) — would introduce unnecessary FFI overhead and complexity.

def safe_get(node, selector, attr='text'):
    el = node.select_one(selector)
    if not el: return ""
    if attr == 'text': return el.get_text().strip()
    return el.get(attr, "").strip()
