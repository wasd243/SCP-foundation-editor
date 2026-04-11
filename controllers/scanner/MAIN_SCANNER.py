import re
from collections import defaultdict

def scan_wikidot(text: str) -> dict:
    """
    扫描 Wikidot 源码，分别提取：
      - css_map : CSS 块内所有以 . 开头的类名 → [行号, ...]
      - div_map : 块外 [[div class="..."]] 里的类名 → [行号, ...]
    """
    css_map: dict[str, list[int]] = defaultdict(list)
    div_map: dict[str, list[int]] = defaultdict(list)

    in_css = False

    # 匹配 CSS 块开头 / 结尾
    RE_CSS_OPEN  = re.compile(r'\[\[\s*module\s+css\s*\]\]', re.IGNORECASE)
    RE_CSS_CLOSE = re.compile(r'\[\[\s*/module\s*\]\]',      re.IGNORECASE)

    # CSS 块内：匹配选择器里以 . 开头的类名（跳过伪类如 :hover）
    # 例: .my-class, .foo.bar::before → 提取 my-class, foo, bar
    RE_CSS_CLASS = re.compile(r'\.([a-zA-Z0-9_-]+)')

    # 块外：匹配 [[div class="foo bar baz"]] 或 [[div class="..."]]
    RE_DIV = re.compile(r'\[\[\s*div\b[^\]]*\bclass\s*=\s*"([^"]*)"', re.IGNORECASE)

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line

        # ── 状态切换（优先于内容提取）──────────────────────────
        if not in_css and RE_CSS_OPEN.search(line):
            in_css = True
            continue   # 开标签行本身不含类名，跳过

        if in_css and RE_CSS_CLOSE.search(line):
            in_css = False
            continue   # 闭标签行同上

        # ── CSS 块内：提取类名 ───────────────────────────────
        if in_css:
            for cls in RE_CSS_CLASS.findall(line):
                css_map[cls].append(line_no)

        # ── 块外：提取 [[div class="..."]] 里的类名 ──────────
        else:
            for m in RE_DIV.finditer(line):
                # class 属性值可能包含多个类名，用空白分割
                for cls in m.group(1).split():
                    div_map[cls].append(line_no)

    return {
        "css_map": dict(css_map),
        "div_map": dict(div_map),
    }


# ── 集成到 MAIN_SCANNER ──────────────────────────────────────────────────────

def scan_code(ui):
    """扫描源代码并打印结构化报告。"""
    if getattr(ui, 'source_display', None) is None:
        print("⚠️ 警告：ui.source_display 不存在")
        return

    code_content = ui.source_display.toPlainText()
    result = scan_wikidot(code_content)

    css_map = result["css_map"]
    div_map = result["div_map"]

    if css_map:
        print(f"\n📦 CSS 块内类名（共 {len(css_map)} 个）:")
        for cls, lines in css_map.items():
            print(f"  .{cls:<30} 出现于行: {lines}")

    if div_map:
        print(f"\n🗂  [[div]] 类名（共 {len(div_map)} 个）:")
        for cls, lines in div_map.items():
            print(f"  {cls:<30} 出现于行: {lines}")

    # 交叉比对：div 引用了哪些 CSS 里定义过的类
    defined   = set(css_map.keys())
    used       = set(div_map.keys())
    matched    = defined & used
    unmatched  = used - defined

    if matched:
        print(f"\n✅ div 引用且 CSS 已定义的类（{len(matched)} 个）: {sorted(matched)}")
    if unmatched:
        print(f"\n⚠️  div 引用但 CSS 未定义的类（{len(unmatched)} 个）: {sorted(unmatched)}")

    return result