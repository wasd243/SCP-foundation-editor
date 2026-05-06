def parse_adv_table(node, state, handle_parse_node):
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
    return None

def parse_table(node, state, handle_parse_node):
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
                if cell.name == 'th':
                    prefix += "~ "
                else:
                    prefix += " "
                line_parts.append(f"{prefix}{content}")
            lines.append(" ".join(line_parts) + " ||")
        return "\n" + "\n".join(lines) + "\n"
    return None