import re

from formats.wikidot.rgb.rgb_to_hex import handle_rgb_to_hex


def parse_span_style(content, style, state):
    if not content.strip():
        return content

    if 'monospace' in style or 'Courier' in style:
        # 等宽字安全逻辑：如果开启且包含中文，则跳过包裹
        if state.get('mono_security') and re.search(r'[\u4e00-\u9fa5]', content):
            return content
        return f"{{{{{content}}}}}"

    res = content
    color_match = re.search(r'color:\s*([^;]+)', style)
    if color_match:
        color_val = handle_rgb_to_hex(color_match.group(1).strip())
        res = f"###{color_val[1:]}|{res}##" if color_val.startswith('#') else f"##{color_val}|{res}##"

    size_match = re.search(r'font-size:\s*([^;]+)', style)
    # 字号处理
    if size_match:
        size_val = size_match.group(1).strip()
        # Wikidot 默认字体大小为 1em 或 medium，其他值都需要显式声明 [[size]] 标签
        default_sizes = ['medium', '1em', 'inherit', 'normal']
        if size_val.lower() not in default_sizes:
            res = f"[[size {size_val}]]{res}[[/size]]"
        if size_val.lower() in default_sizes:
            res = f"{res}"

    if 'underline' in style:
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', res, flags=re.DOTALL)
        if match and match.group(2):
            res = f"{match.group(1)}__{match.group(2)}__{match.group(3)}"

    if 'line-through' in style:
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', res, flags=re.DOTALL)
        if match and match.group(2):
            res = f"{match.group(1)}--{match.group(2)}--{match.group(3)}"

    return res
