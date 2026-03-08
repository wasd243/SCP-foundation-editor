def parse_tabview(node, state, handle_parse_node_func):
    buttons = node.select('.tab-header .tab-btn')
    contents = node.select('.tab-contents .tab-item')
    code = "\n[[tabview]]\n"
    for i, btn in enumerate(buttons):
        title = btn.get_text().strip()
        if i < len(contents):
            tab_body = "".join(handle_parse_node_func(c, state) for c in contents[i].contents).strip()
            code += f"[[tab {title}]]\n{tab_body}\n[[/tab]]\n"
    code += "[[/tabview]]\n"
    return code
