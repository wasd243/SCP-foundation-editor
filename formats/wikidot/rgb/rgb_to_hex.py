import re

def handle_rgb_to_hex(rgb_str):
    if not rgb_str: return ""
    rgb_str = rgb_str.strip()
    if rgb_str.startswith('#'): return rgb_str
    match = re.search(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', rgb_str)
    if match:
        r, g, b = map(int, match.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
    return rgb_str