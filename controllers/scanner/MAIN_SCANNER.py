from controllers.scanner.scan_wikidot import scan_wikidot
import re


# ── 集成到 MAIN_SCANNER ──────────────────────────────────────────────────────


def scan_code(ui, target_module_index=None):
    """扫描源代码并打印结构化报告。
    扫描后会尝试将 CodeMirror 光标跳转到第一个找到的匹配行（如果可用）。
    """
    if getattr(ui, 'source_display', None) is None:
        print("⚠️ 警告：ui.source_display 不存在")
        return

    code_content = ui.source_display.toPlainText()
    result = scan_wikidot(code_content)

    css_map = result.get("css_map", {})
    div_map = result.get("div_map", {})

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

    # 3) 否则回退到原有的 css_map/div_map 优先逻辑
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

    # 执行跳转（如果找到了行号）
    if first_line and getattr(ui, 'source_editor_window', None) is not None:
        try:
            page = ui.source_editor_window.browser.page()
            js = f"if(window.gotoLine) window.gotoLine({first_line});"
            page.runJavaScript(js)
            try:
                ui.source_editor_window.browser.setFocus()
            except Exception:
                pass
        except Exception as e:
            print(f"调用 editor.gotoLine 失败: {e}")

    return result
