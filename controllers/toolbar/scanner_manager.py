import re
from typing import Optional, List, Dict, Any
from controllers.scanner.scan_wikidot import scan_wikidot


class ScannerManager:
    """
    封装 scan_wikidot 的调用，合并 css/div matches，按 offset 排序，
    并选择基于 cursor_pos 的 selected_match 与 first_line（module 优先）。
    不执行任何 JS（由 SyncEngine 负责与前端交互）。
    """

    def __init__(self):
        pass

    def scan(self, code_content: str, target_module_index: Optional[int] = None, cursor_pos: Optional[int] = None) -> Dict[str, Any]:
        """
        返回结构化字典：
          {
            "css_map": {...},
            "div_map": {...},
            "css_matches": [...],
            "div_matches": [...],
            "matches": [...],            # 合并后按 offset 升序
            "selected_match": {...} | None,
            "first_line": int | None
          }
        """
        result = scan_wikidot(code_content or "")

        css_map = result.get("css_map", {})
        div_map = result.get("div_map", {})

        matches: List[Dict[str, Any]] = []
        for css in result.get("css_matches", []):
            matches.append({
                "type": "css",
                "class": css.get("class"),
                "line": css.get("line"),
                "offset": css.get("offset"),
                "end_offset": css.get("end_offset")
            })
        for div in result.get("div_matches", []):
            matches.append({
                "type": "div",
                "class": div.get("class"),
                "line": div.get("line"),
                "offset": div.get("offset"),
                "end_offset": div.get("end_offset")
            })

        # 按偏移排序
        matches.sort(key=lambda x: x.get("offset", 0))

        # 尝试解析 module 的起始行列表（保留 MAIN_SCANNER 的逻辑）
        module_lines: List[int] = []
        try:
            pattern = re.compile(r"\[\[\s*module\b[^\]]*css[^\]]*\]\]", re.I)
            for m in pattern.finditer(code_content or ""):
                ln = (code_content or "").count('\n', 0, m.start()) + 1
                module_lines.append(ln)
        except Exception:
            module_lines = []

        first_line = None
        # 优先使用外部传入的模块索引
        try:
            if target_module_index and module_lines:
                try:
                    idx = int(target_module_index)
                    if 1 <= idx <= len(module_lines):
                        first_line = module_lines[idx - 1]
                    else:
                        first_line = None
                except Exception:
                    first_line = None
        except Exception:
            first_line = None

        # 如果提供 cursor_pos 且存在 matches，优先选择第一个 offset > cursor_pos（下一个），否则 wrap 到第一个
        selected_match = None
        try:
            if cursor_pos is not None and matches:
                next_match = None
                for m in matches:
                    if m.get("offset", 0) > cursor_pos:
                        next_match = m
                        break
                if next_match is None and matches:
                    next_match = matches[0]
                selected_match = next_match
                if selected_match:
                    first_line = selected_match.get("line")
        except Exception:
            selected_match = None

        # 回退到 css_map/div_map 的第一项作为 first_line（如果仍无值）
        if first_line is None:
            try:
                for lines in css_map.values():
                    if lines:
                        first_line = lines[0]
                        break
                if first_line is None:
                    for lines in div_map.values():
                        if lines:
                            first_line = lines[0]
                            break
            except Exception:
                first_line = None

        return {
            "css_map": css_map,
            "div_map": div_map,
            "css_matches": result.get("css_matches", []),
            "div_matches": result.get("div_matches", []),
            "matches": matches,
            "selected_match": selected_match,
            "first_line": first_line
        }
