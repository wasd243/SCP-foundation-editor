from controllers.scanner.scan_wikidot import scan_wikidot
import re
import json


# ── 集成到 MAIN_SCANNER ──────────────────────────────────────────────────────


def scan_code(ui, target_module_index=None, cursor_pos=None):
    """扫描源代码并打印结构化报告。
    扫描后会尝试将 CodeMirror 光标跳转到与当前光标最近/下一个的匹配行（如果可用）。
    参数:
      - ui: UI 实例，必须具有 source_display（文本）和可选的 source_editor_window（CodeMirror窗口）
      - target_module_index: 仍保留兼容行为（1-based 模块索引）
      - cursor_pos: 可选的字符偏移（相对于源码文本的字符索引），用于选择“下一个/最近”的匹配点
    返回:
      - result: scan_wikidot 的返回值，额外包含 "matches" 列表（合并 css/div 的匹配项，按 offset 排序）
    """
    if getattr(ui, 'source_display', None) is None:
        print("⚠️ 警告：ui.source_display 不存在")
        return

    code_content = ui.source_display.toPlainText()
    result = scan_wikidot(code_content)

    css_map = result.get("css_map", {})
    div_map = result.get("div_map", {})

    # 输出简洁报告（保留）
    if css_map:
        print(f"\n📦 CSS 块内类名（共 {len(css_map)} 个）:")
        for cls, lines in css_map.items():
            print(f"  .{cls:<30} 出现于行: {lines}")

    if div_map:
        print(f"\n🗂  [[div]] 类名（共 {len(div_map)} 个）:")
        for cls, lines in div_map.items():
            print(f"  {cls:<30} 出现于行: {lines}")

    # 交叉比对：div 引用了哪些 CSS 里定义过的类
    defined = set(css_map.keys())
    used = set(div_map.keys())
    matched = defined & used
    unmatched = used - defined

    if matched:
        print(f"\n✅ div 引用且 CSS 已定义的类（{len(matched)} 个）: {sorted(matched)}")
    if unmatched:
        print(f"\n⚠️  div 引用但 CSS 未定义的类（{len(unmatched)} 个）: {sorted(unmatched)}")

    # --------------------------------------------------------------------
    # 构造统一的 matches 列表，包含所有匹配项（带 offset、line）
    # --------------------------------------------------------------------
    matches = []
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

    # 根据 target_module_index 优先跳转到指定 [[module css]] 模块的起始行（如果可用）
    first_line = None

    # 1) 解析所有 [[module ...css...]] 的起始行号（1-based）
    module_lines = []
    try:
        pattern = re.compile(r"\[\[\s*module\b[^\]]*css[^\]]*\]\]", re.I)
        for m in pattern.finditer(code_content):
            ln = code_content.count('\n', 0, m.start()) + 1
            module_lines.append(ln)
    except Exception:
        module_lines = []

    # 2) 如果外部传入了模块索引，优先使用它
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

    # 3) 如果提供了 cursor_pos 且有 matches，优先选择“下一个”匹配（offset > cursor_pos），否则循环到第一个
    selected_match = None
    try:
        if cursor_pos is not None and matches:
            # 找到第一个 offset > cursor_pos
            next_match = None
            for m in matches:
                if m.get("offset", 0) > cursor_pos:
                    next_match = m
                    break
            if next_match is None:
                # 循环：如果没有找到更后的匹配，wrap 到第一个
                next_match = matches[0]
            selected_match = next_match
            first_line = selected_match.get("line")
    except Exception:
        selected_match = None

    # 4) 否则回退到原有的 css_map/div_map 优先逻辑（如果 first_line 仍为 None）
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

    # 执行跳转（如果找到了行号）——优先使用前端的 gotoMatchList（把所有 matches 发过去）
    if matches and getattr(ui, 'source_editor_window', None) is not None:
        try:
            page = ui.source_editor_window.browser.page()
            matches_json = json.dumps(matches)
            # 优先调用 window.gotoMatchList，让前端根据其实时光标位置决定跳转。
            # 退回逻辑：如果没有该函数则调用 gotoLine（使用 first_line）。
            js = f"""
try {{
    if (typeof window.gotoMatchList === 'function') {{
        window.gotoMatchList({matches_json});
    }} else if (typeof window.gotoLine === 'function') {{
        window.gotoLine({first_line if first_line is not None else 1});
    }}
}} catch(e) {{
    console.error('scan_code -> js run error', e);
}}
"""
            page.runJavaScript(js)
            try:
                ui.source_editor_window.browser.setFocus()
            except Exception:
                pass
        except Exception as e:
            print(f"调用 editor.gotoMatchList/ gotoLine 失败: {e}")
    else:
        # 若没有 matches 或 source_editor_window，不做 JS 调用，仅打印信息
        if first_line:
            print(f"跳转目标：第 {first_line} 行（JS 窗口不可用或 matches 为空）")

    # 把 matches 放入返回结果，供调用者使用
    result["matches"] = matches
    result["selected_match"] = selected_match

    return result
