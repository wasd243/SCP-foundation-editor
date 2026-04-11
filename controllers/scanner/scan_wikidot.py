import re
from collections import defaultdict
from typing import List, Dict, Any


def scan_wikidot(text: str) -> dict:
    """
    扫描 Wikidot 源码，分别提取：
      - css_map : CSS 块内所有以 . 开头的类名 -> [line_no, ...]  （保持向后兼容）
      - div_map : 块外 [[div class="..."]] 里的类名 -> [line_no, ...] （保持向后兼容）
      - css_matches : 列表，包含 CSS 块内每个类名的详细匹配项：
            { "class": str, "line": int, "offset": int, "end_offset": int }
      - div_matches : 列表，包含 div class 属性内每个类名的详细匹配项：
            { "class": str, "line": int, "offset": int, "end_offset": int }
    注：offset 与 end_offset 是相对于全文（text）的字符偏移，line 为 1-based 行号。
    """
    css_map: Dict[str, List[int]] = defaultdict(list)
    div_map: Dict[str, List[int]] = defaultdict(list)

    css_matches: List[Dict[str, Any]] = []
    div_matches: List[Dict[str, Any]] = []

    in_css = False

    # 匹配 CSS 块开头 / 结尾
    RE_CSS_OPEN = re.compile(r'\[\[\s*module\s+css\s*\]\]', re.IGNORECASE)
    RE_CSS_CLOSE = re.compile(r'\[\[\s*/module\s*\]\]', re.IGNORECASE)

    # CSS 块内：匹配选择器里以 . 开头的类名（跳过伪类如 :hover）
    RE_CSS_CLASS = re.compile(r'\.([a-zA-Z0-9_-]+)')

    # 块外：匹配 [[div ... class="foo bar"]]
    RE_DIV = re.compile(r'\[\[\s*div\b[^\]]*\bclass\s*=\s*"([^"]*)"', re.IGNORECASE)

    # 为了计算全局字符偏移，逐行迭代但保留换行符以便精确计算偏移
    cumulative_offset = 0
    lines = text.splitlines(True)  # True -> 保留换行符

    for idx, raw_line in enumerate(lines, start=1):
        # raw_line 包含行尾换行（如果有）
        line_start_offset = cumulative_offset
        # 为了按行匹配，使用不包含行尾换行的文本
        line_text = raw_line.rstrip('\n').rstrip('\r')

        # 状态切换（优先）
        if not in_css and RE_CSS_OPEN.search(line_text):
            in_css = True
            cumulative_offset += len(raw_line)
            continue

        if in_css and RE_CSS_CLOSE.search(line_text):
            in_css = False
            cumulative_offset += len(raw_line)
            continue

        # CSS 块内：提取类名（并记录偏移）
        if in_css:
            for m in RE_CSS_CLASS.finditer(line_text):
                cls = m.group(1)
                css_map[cls].append(idx)
                start = line_start_offset + m.start(1)  # 指向类名开头，不包含点
                end = line_start_offset + m.end(1)
                css_matches.append({
                    "class": cls,
                    "line": idx,
                    "offset": start,
                    "end_offset": end
                })

        # 块外：提取 [[div class="..."]] 里的类名（可能有多个）
        else:
            for m in RE_DIV.finditer(line_text):
                group_start = line_start_offset + m.start(1)
                group_text = m.group(1)
                # 找到 group_text 中的每个 token（类名），记录相对位置
                for token_match in re.finditer(r'\S+', group_text):
                    cls = token_match.group(0)
                    token_start = group_start + token_match.start()
                    token_end = group_start + token_match.end()
                    div_map[cls].append(idx)
                    div_matches.append({
                        "class": cls,
                        "line": idx,
                        "offset": token_start,
                        "end_offset": token_end
                    })

        cumulative_offset += len(raw_line)

    return {
        "css_map": dict(css_map),
        "div_map": dict(div_map),
        "css_matches": css_matches,
        "div_matches": div_matches,
    }
