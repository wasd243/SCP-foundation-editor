def safe_get(node, selector, attr='text'):
    el = node.select_one(selector)
    if not el: return ""
    if attr == 'text': return el.get_text().strip()
    return el.get(attr, "").strip()
