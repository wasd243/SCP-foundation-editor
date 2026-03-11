import re
from bs4 import BeautifulSoup, NavigableString

from formats.wikidot.rgb.rgb_to_hex import handle_rgb_to_hex

def rgb_to_hex(rgb_str):
    return handle_rgb_to_hex(rgb_str)

def handle_parse_node(node, state):
    """
    核心正向解析器 (已剥离 UI 和 self)
    将 HTML 节点递归转换为 Wikidot 语法
    
    :param node: BeautifulSoup 节点 (Tag 或 NavigableString)
    :param state: 解析状态字典，用于跨层级记录上下文传递 (例如是否在粗体/斜体内部、是否开启了特殊选项)
    :return: 转换后的 Wikidot 代码字符串
    """
    def safe_get(selector, attr='text'):
        el = node.select_one(selector)
        if not el: return ""
        if attr == 'text': return el.get_text().strip()
        return el.get(attr, "").strip()

    if isinstance(node, NavigableString): return str(node)

    # --- Advanced Wikidot [[table]] export ---
    if node.get('class') and 'wikidot-adv-table' in node.get('class', []):
        tbl_style = node.get('data-wd-style', '')
        tbl_style_part = f' style="{tbl_style}"' if tbl_style else ''
        lines = [f'[[table{tbl_style_part}]]']
        all_rows = []
        for child in node.children:
            if hasattr(child, 'name'):
                if child.name == 'tr':
                    all_rows.append(child)
                elif child.name in ['tbody', 'thead', 'tfoot']:
                    all_rows.extend(child.find_all('tr', recursive=False))
        for tr in all_rows:
            row_style = tr.get('data-wd-style', '')
            row_style_part = f' style="{row_style}"' if row_style else ''
            lines.append(f'[[row{row_style_part}]]')
            for cell in tr.find_all(['td', 'th'], recursive=False):
                cell_style = cell.get('data-wd-style', '')
                cell_style_part = f' style="{cell_style}"' if cell_style else ''
                inner = ''.join(handle_parse_node(c, state) for c in cell.contents).strip()
                lines.append(f'[[cell{cell_style_part}]]')
                if inner: lines.append(inner)
                lines.append('[[/cell]]')
            lines.append('[[/row]]')
        lines.append('[[/table]]')
        return '\n' + '\n'.join(lines) + '\n'

    if node.name == 'table':
        lines = []
        all_rows = []
        for child in node.children:
            if child.name == 'tr':
                all_rows.append(child)
            elif child.name in ['tbody', 'thead', 'tfoot']:
                all_rows.extend(child.find_all('tr', recursive=False))

        for tr in all_rows:
            line_parts = []
            for cell in tr.find_all(['td', 'th'], recursive=False):
                colspan = int(cell.get('colspan', '1'))
                prefix = "||" * colspan
                content = "".join(handle_parse_node(c, state) for c in cell.contents).strip()
                content = content.replace('\n', ' _\n')
                if cell.name == 'th': prefix += "~ "
                else: prefix += " "
                line_parts.append(f"{prefix}{content}")
            lines.append(" ".join(line_parts) + " ||")
        return "\n" + "\n".join(lines) + "\n"

    if node.get('class') and 'scp-component' in node.get('class'):
        c_type = node.get('data-type')
        
        # ==========================================
        # 🟢 本地自定义组件解析区 (SCP Component)
        # 将被包装过的块级自定义组件还原为它本身的 Wikidot 语法。
        # 每一种 c_type 对应一个拦截器生成的标记或者特殊的可视化节点。
        # ==========================================

        from .components import COMPONENT_PARSERS
        
        parser_func = COMPONENT_PARSERS.get(c_type)
        if parser_func:
            return parser_func(node, state, handle_parse_node)

    # ==========================================
    # 🔵 标准 HTML 标签 / 原生文本 解析区
    # 处理加粗、斜体、列表、引用框等基础标签
    # ==========================================

    tag = node.name
    inner_state = state
    if tag in ['b', 'strong']:
        if state.get('in_bold'): return "".join(handle_parse_node(child, state) for child in node.contents)
        inner_state = state.copy()
        inner_state['in_bold'] = True
    elif tag in ['i', 'em']:
        if state.get('in_italic'): return "".join(handle_parse_node(child, state) for child in node.contents)
        inner_state = state.copy()
        inner_state['in_italic'] = True

    content = "".join(handle_parse_node(child, inner_state) for child in node.contents)
    content = content.replace('\u200b', '')

    if tag == 'p':
        def expand_soft_breaks(match):
            count = len(match.group(0))
            if count <= 2:
                return "\n" * count
            # 保留一个\n作为段落分隔，后面紧连(N-2)个@@@@
            return "\n" + ("@@@@\n" * (count - 2))
        content = re.sub(r'\n{2,}', expand_soft_breaks, content)
        clean = content.replace('**', '').replace('//', '').replace('__', '').replace('^^', '').replace(',,', '').strip()
        if not clean: return "\n@@@@\n"
    
    if tag == 'br': return "\n"
    if tag == 'hr': return "\n------\n"

    style = node.get('style', '') if hasattr(node, 'get') else ''
    align_mark = ""
    if 'text-align: right' in style or 'text-align:right' in style: align_mark = ">"
    elif 'text-align: left' in style or 'text-align:left' in style: align_mark = "<"
    elif 'text-align: center' in style or 'text-align:center' in style: align_mark = "="

    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(tag[1])
        return f"\n{'+' * level} {content.strip()}\n"

    if tag == 'span' and 'custom-dash' in node.get('class', []):
        try: count = int(node.get('data-count', '6'))
        except ValueError: count = 6
        return f'@{"-" * count}@'

    if tag == 'span' and node.has_attr('style'):
        if not content.strip(): return content
        if 'monospace' in style or 'Courier' in style: return f"{{{{{content}}}}}"
        res = content
        color_match = re.search(r'color:\s*([^;]+)', style)
        if color_match:
            color_val = rgb_to_hex(color_match.group(1).strip())
            res = f"###{color_val[1:]}|{res}##" if color_val.startswith('#') else f"##{color_val}|{res}##"
        size_match = re.search(r'font-size:\s*([\w\.\-%]+)', style)
        if size_match: 
            size_val = size_match.group(1).strip()
            if size_val.lower() not in ['medium', '1em']:
                res = f"[[size {size_val}]]{res}[[/size]]"
        if 'underline' in style:
            match = re.fullmatch(r'(\s*)(.*?)(\s*)', res, flags=re.DOTALL)
            if match and match.group(2): res = f"{match.group(1)}__{match.group(2)}__{match.group(3)}"
        if 'line-through' in style:
            match = re.fullmatch(r'(\s*)(.*?)(\s*)', res, flags=re.DOTALL)
            if match and match.group(2): res = f"{match.group(1)}--{match.group(2)}--{match.group(3)}"
        return res

    if tag == 'font':
        if not content.strip(): return content
        res = content
        if node.has_attr('color'): res = f"##{node['color']}|{res}##"
        return res

    if tag == 'sup': 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)}^^{match.group(2)}^^{match.group(3)}"
        return content
    if tag == 'sub': 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)},,{match.group(2)},,{match.group(3)}"
        return content
    if tag == 'u': 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)}__{match.group(2)}__{match.group(3)}"
        return content
    if tag in ['s', 'strike', 'del']: 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)}--{match.group(2)}--{match.group(3)}"
        return content

    if tag == 'li':
        parent = node.parent
        return f"* {content.strip()}\n" if parent.name == 'ul' else f"# {content.strip()}\n"

    if tag == 'blockquote':
        lines = content.split('\n')
        return "".join(f"> {line}\n" for line in lines) + "\n"

    if tag == 'a':
        href = node.get('href')
        prefix = "*" if node.get('target') == '_blank' else ""
        return f"[{prefix}{href} {content.strip()}]"

    if tag == 'p':
        val = f"{content}\n"
        if align_mark: return f"[[{align_mark}]]\n{content.strip()}\n[[/{align_mark}]]\n"
        return val

    if tag == 'div':
        # Build parameters for class and style
        params_list = []
        if node.has_attr('class'):
            cls = " ".join(c for c in node['class'] if c not in ['scp-component', 'div-content', 'div-header', 'basalt-theme', 'bhl-theme', 'shivering-theme', 'raisa-box', 'class-warning-box', 'terminal-001-box', 'terminal-shortcut-box', 'o5-box', 'foundation-bg-box', 'page-note-box'])
            if cls: params_list.append(f'class="{cls}"')
            elif not node.has_attr('style'):
                # If it only had excluded classes and no styling, return raw content
                res = content
                if align_mark: return f"[[{align_mark}]]\n{res.strip()}\n[[/{align_mark}]]\n"
                return res
                
        if node.has_attr('style') and node['style'].strip():
            # We must strip text-align out since align_mark will handle it
            style_clean = re.sub(r'text-align:\s*(center|left|right);?', '', node['style'])
            if style_clean.strip():
                params_list.append(f'style="{style_clean.strip()}"')
            
        if params_list:
            params_str = " ".join(params_list)
            res = f"[[div {params_str}]]\n{content}\n[[/div]]\n"
        else:
            # Fallback to pure text cleaning if no useful attributes
            clean = content.replace('**', '').replace('//', '').replace('__', '').replace('^^', '').replace(',,', '').strip()
            if not clean: return "\n@@@@\n"
            def expand_soft_breaks(match):
                count = len(match.group(0))
                if count <= 2:
                    return "\n" * count
                return "\n" + ("@@@@\n" * (count - 2))
            res = re.sub(r'\n{2,}', expand_soft_breaks, content) + "\n"

        if align_mark: 
            return f"[[{align_mark}]]\n{res.strip()}\n[[/{align_mark}]]\n"
        return res
            
        # Fallback to pure text cleaning if no useful attributes
        clean = content.replace('**', '').replace('//', '').replace('__', '').replace('^^', '').replace(',,', '').strip()
        if not clean: return "\n@@@@\n"
        def expand_soft_breaks(match):
            count = len(match.group(0))
            if count <= 2:
                return "\n" * count
            return "\n" + ("@@@@\n" * (count - 2))
        content_fixed = re.sub(r'\n{2,}', expand_soft_breaks, content)
        return f"{content_fixed}\n"

    if tag in ['b', 'strong']: return f"**{content}**" if content.strip() else content
    if tag in ['i', 'em']: return f"//{content}//" if content.strip() else content
    if tag == 'style':
        return f"\n[[module CSS]]\n{content.strip()}\n[[/module]]\n"
        
    return content
