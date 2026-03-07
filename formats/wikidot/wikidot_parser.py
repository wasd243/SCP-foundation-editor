import re
import sys
import os
import html as _html_module

# 注入项目根目录以允许导入 engine.process.interceptor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import ftml_py
    HAS_FTML = True
    print("[OK] 成功加载 ftml_py")
except ImportError:
    HAS_FTML = False
    print("[WARNING] 警告: 未找到 ftml_py，回退到基础纯文本模式")

try:
    from engine.process.interceptor.MAIN_INTERCEPTOR import ComponentInterceptor
except ImportError:
    try:
        # 尝试从当前目录导入 (如果脚本被直接运行)
        from engine.process.interceptor.MAIN_INTERCEPTOR import ComponentInterceptor
    except ImportError:
        ComponentInterceptor = None
        print("⚠️ 警告: 未找到 interceptor 模块，组件双向绑定库可能失效")

# =====================================================================
# 页面元数据提取 (完全保留，用于控制界面的勾选框)
# =====================================================================
def parse_wikidot_code(code: str) -> dict:
    result = {
        "themes": {
            "basalt": False, "basalt_dark": False, "basalt_wide": False, "basalt_hidetitle": False,
            "shivering_night": False, "shivering_sub": "default",
            "bhl": False, "bhl_dark_sidebar": False, "bhl_collapsible": False, "bhl_toggle": False, "bhl_centered": False, "bhl_office": False,
        },
        "better_footnotes": False,
        "rate_module": {"hidden": True, "align": ""},
        "css": ""
    }

    if not code or not code.strip(): return result

    if "theme:basalt" in code:
        result["themes"]["basalt"] = True
        if "darkmode=a" in code: result["themes"]["basalt_dark"] = True
        if "wide=a" in code: result["themes"]["basalt_wide"] = True
        if "hidetitle=a" in code: result["themes"]["basalt_hidetitle"] = True
    elif "theme:shivering-night" in code:
        result["themes"]["shivering_night"] = True
        if "theme:shivering-night-macau" in code: result["themes"]["shivering_sub"] = "macau"
        elif "theme:shivering-night-kuala-lumpur" in code: result["themes"]["shivering_sub"] = "kl"
        elif "theme:shivering-night-dublin" in code: result["themes"]["shivering_sub"] = "dub"
        elif "theme:shivering-night-cape-town" in code: result["themes"]["shivering_sub"] = "ct"
        elif "theme:shivering-night-buenos-aires" in code: result["themes"]["shivering_sub"] = "ba"
    elif "theme:black-highlighter-theme" in code:
        result["themes"]["bhl"] = True
        if ":component:bhl-dark-sidebar" in code: result["themes"]["bhl_dark_sidebar"] = True
        if ":component:collapsible-sidebar" in code: result["themes"]["bhl_collapsible"] = True
        if ":component:toggle-sidebar-bhl" in code: result["themes"]["bhl_toggle"] = True
        if ":component:centered-header-bhl" in code: result["themes"]["bhl_centered"] = True
        if "theme:scp-offices-theme" in code: result["themes"]["bhl_office"] = True

    if ":component:betterfootnotes" in code: result["better_footnotes"] = True

    if re.search(r'\[\[module Rate\]\]', code, re.IGNORECASE):
        result["rate_module"]["hidden"] = False
        if re.search(r'\[\[<\]\]\s*\[\[module Rate\]\]\s*\[\[/<\]\]', code, re.IGNORECASE): result["rate_module"]["align"] = "left"
        elif re.search(r'\[\[>\]\]\s*\[\[module Rate\]\]\s*\[\[/>\]\]', code, re.IGNORECASE): result["rate_module"]["align"] = "right"

    extracted_css = ""
    css_matches = re.finditer(r'\[\[module CSS\]\](.*?)\[\[/module\]\]', code, flags=re.DOTALL|re.IGNORECASE)
    for m in css_matches: extracted_css += m.group(1).strip() + "\n"
    result["css"] = extracted_css
    return result


# =====================================================================
# 核心解析器：混合管线 (拦截强交互组件 -> 委托 Rust 渲染排版)
# =====================================================================
def parse_wikidot_to_editor_html(text: str, theme_type: str = "none") -> str:
    if not text.strip(): return ""

    text = _html_module.unescape(text)
    
    # 基础空行清理
    text = re.sub(r'<p>\s*<br\s*/?>\s*</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
    _has_basalt_in_source = (
        ":theme:basalt" in text.lower() or 
        "theme='basalt'" in text.lower() or 
        'theme="basalt"' in text.lower()
    )

    placeholders = {}
    ph_count = 0
    def register_ph(html_content):
        nonlocal ph_count
        token = f"WDKEY{ph_count}ENDWDKEY"
        placeholders[token] = html_content
        ph_count += 1
        return token

    def register_forced_break(source):
        html = f'<p class="forced-break" data-source="{source}" contenteditable="false" style="display: block; width: 100%; height: 0em; min-height: 0; border: 1px dashed transparent; margin: 0;"></p>'
        return register_ph(html)

    # 1. 交给 ftml 原生解析
    def process_terminal_source(txt):
        # 暂时关闭检测用户输入的注入，交给 ftml 反向解析
        pass
        return txt
    
    text = process_terminal_source(text)

    # 2. 恢复 OLD 的 Fakeprot
    def process_fakeprot_source(txt):
        # 暂时关闭检测用户输入的注入，交给 ftml 反向解析
        pass
        return txt
        
    text = process_fakeprot_source(text)

    # 3. 恢复 OLD 的 Wikidot 表格
    def wikidot_table_replacer(txt):
        # result = []
        # cursor = 0
        # pat_tbl_start = re.compile(r'\[\[table(\s[^\]]*)?\]\]', re.IGNORECASE)
        # pat_tbl_end = re.compile(r'\[\[/table\]\]', re.IGNORECASE)
        # pat_row = re.compile(r'\[\[row(\s[^\]]*)?\]\]', re.IGNORECASE)
        # pat_row_end = re.compile(r'\[\[/row\]\]', re.IGNORECASE)
        # pat_cell = re.compile(r'\[\[cell(\s[^\]]*)?\]\]', re.IGNORECASE)
        # pat_cell_end = re.compile(r'\[\[/cell\]\]', re.IGNORECASE)

        # for m_tbl in pat_tbl_start.finditer(txt):
        #     tbl_start = m_tbl.start()
        #     if tbl_start < cursor: continue
        #     m_tend = pat_tbl_end.search(txt, m_tbl.end())
        #     if not m_tend: continue
        #     tbl_end = m_tend.end()

        #     tbl_params = (m_tbl.group(1) or '').strip()
        #     inner_txt = txt[m_tbl.end(): m_tend.start()]

        #     rows_html = ''
        #     row_cursor = 0
        #     for m_row in pat_row.finditer(inner_txt):
        #         if m_row.start() < row_cursor: continue
        #         m_rend = pat_row_end.search(inner_txt, m_row.end())
        #         if not m_rend: continue

        #         row_params = (m_row.group(1) or '').strip()
        #         row_inner = inner_txt[m_row.end(): m_rend.start()]

        #         row_style_m = re.search(r'style=["\']([^"\']*)["\']', row_params, re.IGNORECASE)
        #         row_style = row_style_m.group(1) if row_style_m else ''
        #         row_style_attr = f' style="{row_style}"' if row_style else ''
        #         row_data = f' data-wd-style="{row_style}"' if row_style else ''

        #         cells_html = ''
        #         cell_cursor = 0
        #         for m_cell in pat_cell.finditer(row_inner):
        #             if m_cell.start() < cell_cursor: continue
        #             m_cend = pat_cell_end.search(row_inner, m_cell.end())
        #             if not m_cend: continue

        #             cell_params = (m_cell.group(1) or '').strip()
        #             cell_inner_raw = row_inner[m_cell.end(): m_cend.start()].strip()

        #             cell_style_m = re.search(r'style=["\']([^"\']*)["\']', cell_params, re.IGNORECASE)
        #             cell_style = cell_style_m.group(1) if cell_style_m else ''
        #             cell_style_attr = f' style="{cell_style}"' if cell_style else ''
        #             cell_data = f' data-wd-style="{cell_style}"' if cell_style else ''

        #             parsed_cell = parse_wikidot_to_editor_html(cell_inner_raw, theme_type)
        #             cells_html += f'<td{cell_style_attr}{cell_data} contenteditable="true">{parsed_cell}</td>'
        #             cell_cursor = m_cend.end()

        #         rows_html += f'<tr{row_style_attr}{row_data}>{cells_html}</tr>'
        #         row_cursor = m_rend.end()

        #     tbl_style_m = re.search(r'style=["\']([^"\']*)["\']', tbl_params, re.IGNORECASE)
        #     tbl_style = tbl_style_m.group(1) if tbl_style_m else ''
        #     tbl_style_attr = f' style="{tbl_style}"' if tbl_style else ''
        #     tbl_data = f' data-wd-style="{tbl_style}"' if tbl_style else ''

        #     tbl_html = (
        #         f'<table class="scp-component wikidot-adv-table" data-type="wikidot-table"'
        #         f'{tbl_style_attr}{tbl_data} contenteditable="false">'
        #         f'<tbody>{rows_html}</tbody></table>'
        #     )
        #     result.append(txt[cursor: tbl_start])
        #     result.append(register_ph(tbl_html))
        #     cursor = tbl_end

        # result.append(txt[cursor:])
        # return ''.join(result)
        pass 
        return txt
    
    text = wikidot_table_replacer(text)

    # 4. 玄武岩专用 DIV 及 其他特定 DIV - 暂时交给 ftml 原生解析
    def process_special_divs(txt):
        # 暂时关闭检测用户输入的注入，交给 ftml 反向解析
        pass
        return txt

    text = process_special_divs(text)

    # 5. 音频播放器
    def audio_replacer(match):
        audio_url = match.group(1).strip()
        html = f'<div class="scp-component html5player-box" data-type="html5player" contenteditable="false"><audio controls src="{audio_url}"></audio><span class="html5player-url" style="display:none;">{audio_url}</span></div>'
        return register_ph(html)
    text = re.sub(r'\[\[include\s+:snippets:html5player\s*\|type=audio\s*\|url=(.*?)\]\]', audio_replacer, text, flags=re.IGNORECASE)

    # ========================================================
    # 阶段 2：拦截器 (ACS, AIM, 脚注, License, 图片块, Tabview, User, div, css等)
    # ========================================================
    store = None
    if ComponentInterceptor:
        interceptor = ComponentInterceptor()
        text, store = interceptor.intercept(text, theme_type, parse_wikidot_to_editor_html)

    # ========================================================
    # 阶段 3：Rust 底层引擎接管
    # ========================================================
    if HAS_FTML:
        try:
            html_output = ftml_py.render_wikidot_to_html(text)
            html_output = html_output.replace('<table class="wiki-content-table">', '<table border="1" class="wikidot-table">')
            html_output = html_output.replace('<td', '<td contenteditable="true"')
            html_output = html_output.replace('<th', '<th contenteditable="true"')
        except Exception as e:
            print(f"❌ ftml 解析失败: {e}")
            html_output = _fallback_basic_parse(text)
    else:
        html_output = _fallback_basic_parse(text)

    # ========================================================
    # 阶段 4：占位符与金库还原
    # ========================================================
    if store:
        for comp_uuid, comp in store.get_all().items():
            if comp['type'] == 'css-module':
                # 先让 ftml 原生解析，不进行基于 marker 的注入
                pass
            elif comp['type'] == 'div-block':
                # 先让 ftml 原生解析，不进行基于 marker 的注入
                pass
            elif comp['type'] == 'collapsible':
                # 先让 ftml 原生解析，不进行基于 marker 的注入
                pass
            else:
                ph = f"WDKEY{comp_uuid}ENDWDKEY"
                html_output = html_output.replace(f"<p>{ph}</p>", comp['html'])
                html_output = html_output.replace(ph, comp['html'])

    for k in reversed(list(placeholders.keys())):
        html_output = html_output.replace(f"<p>{k}</p>", placeholders[k])
        html_output = html_output.replace(k, placeholders[k])

    return html_output

    return html_output


def _fallback_basic_parse(text: str) -> str:
    """极其基础的正则兜底 (防崩溃)"""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!:)//(.*?)//', r'<i>\1</i>', text)
    text = text.replace('\n', '<br>')
    return text