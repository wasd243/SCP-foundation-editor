import re

def parse_div_block(node, state, handle_parse_node_func):
    header_node = node.select_one('.div-header')
    content_node = node.select_one('.div-content')
    
    if header_node and content_node:
        params = header_node.get_text().replace('DIV:', '').strip()
        if params.startswith('[[div') and params.endswith(']]'):
            params = params[5:-2].strip()
        inner = "".join(handle_parse_node_func(c, state) for c in content_node.contents).strip()
    else:
        source = node.get('data-source', '')
        params = ''
        if source.startswith('[[div'):
            m = re.search(r'^\[\[div\s+([^\]]+)\]\]', source, re.IGNORECASE)
            if m:
                params = m.group(1).strip()
        if not params:
            # Fallback if source fails
            classes = [c for c in node.get('class', []) if c not in ['scp-component', 'div-block', 'terminal-shortcut-box'] and not c.startswith('WDUUID_')]
            params = f'class="{" ".join(classes)}"' if classes else ''
        
        # Natively rendered ftml div - its children are its content
        inner = "".join(handle_parse_node_func(c, state) for c in node.contents).strip()

    return f"\n[[div {params}]]\n{inner}\n[[/div]]\n"
