import re
import sys
import os
import urllib.parse
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
        "css": "",
        "has_toc": False
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

    if re.search(r'\[\[toc\]\]', code, re.IGNORECASE):
        result["has_toc"] = True

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
    
    # 【修复 1】：智能保护 @@...@@ 原生标签
    # 将包含实质内容的 @@代码@@ 保护为占位符；
    # 将空的 @@@@ 或 @@ @@ 标记为特殊空块占位符 EMPTY_RAW_TOKEN，它最终会被转为原生的 HTML 空行，完美对接导出的换行逻辑。
    RAW_PROTECT_TOKEN_START = "WDKEY_RAW_START_TOKEN"
    RAW_PROTECT_TOKEN_END = "WDKEY_RAW_END_TOKEN"
    EMPTY_RAW_TOKEN = "WDKEY_EMPTY_RAW_TOKEN"

    def raw_protect_cb(match):
        inner = match.group(1)
        if not inner.strip():
            # 这是一个空的 raw block (如 @@@@)，用于强制换行
            return EMPTY_RAW_TOKEN
        return f"{RAW_PROTECT_TOKEN_START}{inner}{RAW_PROTECT_TOKEN_END}"
    
    text = re.sub(r'@@(.*?)@@', raw_protect_cb, text, flags=re.DOTALL)

    # 检测主题
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

    # 1. 交给 ftml 原生解析
    def process_terminal_source(txt):
        pass
        return txt
    
    text = process_terminal_source(text)

    # 2. 恢复 OLD 的 Fakeprot
    def process_fakeprot_source(txt):
        pass
        return txt
        
    text = process_fakeprot_source(text)

    # 3. 恢复 OLD 的 Wikidot 表格
    def wikidot_table_replacer(txt):
        pass 
        return txt
    
    text = wikidot_table_replacer(text)

    # 4. 玄武岩专用 DIV 及 其他特定 DIV - 暂时交给 ftml 原生解析
    def process_special_divs(txt):
        pass
        return txt

    text = process_special_divs(text)

    # 5. 音频播放器
    def audio_replacer(match):
        audio_url = match.group(1).strip()
        html = f'<div class="scp-component html5player-box" data-type="html5player" contenteditable="false"><audio controls src="{audio_url}"></audio><span class="html5player-url" style="display:none;">{audio_url}</span></div>'
        return register_ph(html)
    text = re.sub(r'\[\[include\s+:snippets:html5player\s*\|type=audio\s*\|url=(.*?)\]\]', audio_replacer, text, flags=re.IGNORECASE)

    # 6. 处理标题标记... (或其他后续逻辑)

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
            
            # 使用 BS4 对特定格式组件的输出结构进行保护和注入 contenteditable
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_output, 'html.parser')

            # Terminal Shortcut
            for div in soup.find_all('div', class_=lambda c: c and 'danke' in c and 'agent' in c):
                div['class'] = div.get('class', []) + ['scp-component', 'terminal-shortcut-box']
                div['data-type'] = 'div-block'
                div['contenteditable'] = 'false'
                for p in div.find_all('p'): p['contenteditable'] = 'true'

            # Terminal 001
            for div in soup.find_all('div', class_=lambda c: c and 'terminal' in c and 'scp-component' not in c):
                div['class'] = div.get('class', []) + ['scp-component', 'terminal-001-box']
                div['data-type'] = 'div-block'
                div['contenteditable'] = 'false'
                for text_div in div.find_all('div', class_='text'):
                    text_div['contenteditable'] = 'true'

            # Raisa Notice
            for div in soup.find_all('div', style=lambda s: s and 'border:solid 1px #999999' in s and 'background:#f2f2c2' in s):
                div['class'] = div.get('class', []) + ['scp-component', 'raisa-box']
                div['data-type'] = 'div-block'
                div['contenteditable'] = 'false'
                for p in div.find_all('p'):
                    if p.text.strip(): p['contenteditable'] = 'true'

            # Class Warning
            for div in soup.find_all('div', style=lambda s: s and 'the-great-hippo/scp_trans.png' in s):
                div['class'] = div.get('class', []) + ['scp-component', 'class-warning-box']
                div['data-type'] = 'div-block'
                div['contenteditable'] = 'false'
                for p in div.find_all('p'):
                    if p.text.strip(): p['contenteditable'] = 'true'

            # O5 Command
            for div in soup.find_all('div', style=lambda s: s and 'kaktuskontainer' in s and 'scp_trans.png' in s):
                div['class'] = div.get('class', []) + ['scp-component', 'o5-box']
                div['data-type'] = 'div-block'
                div['contenteditable'] = 'false'
                for child in div.find_all(['p', 'div'], recursive=False):
                    if child.text.strip():
                        # 把这层设置为可编辑，同时也把内部可能存在的层级设置，确保 span 没有阻挡点击
                        child['contenteditable'] = 'true'
                        for span in child.find_all('span'):
                            if span.text.strip():
                                span['contenteditable'] = 'true'
                        for h in child.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong']):
                            h['contenteditable'] = 'true'

            # Foundation Background
            for div in soup.find_all('div', class_='orderwrapper'):
                div['class'] = div.get('class', []) + ['scp-component', 'foundation-bg-box']
                div['data-type'] = 'div-block'
                div['contenteditable'] = 'false'
                
                title_div = div.find('div', class_='ordertitle')
                if title_div:
                    title_div['contenteditable'] = 'true'
                    for child in title_div.find_all(['h1', 'h2', 'span', 'strong']): child['contenteditable'] = 'true'
                
                desc_div = div.find('div', class_='orderdescription')
                if desc_div:
                    desc_div['contenteditable'] = 'true'
                    for child in desc_div.find_all(['p', 'h1', 'h2', 'span', 'strong']): child['contenteditable'] = 'true'
                        
                itemno_div = div.find('div', class_='itemno')
                if itemno_div:
                    itemno_div['contenteditable'] = 'true'
                    for child in itemno_div.find_all(['h1', 'h2', 'span', 'strong']): child['contenteditable'] = 'true'
            
            # Page Note (便签纸)
            for div in soup.find_all('div', class_='page'):
                div['class'] = div.get('class', []) + ['scp-component', 'page-note-box']
                div['data-type'] = 'div-block'
                div['contenteditable'] = 'true'
                for child in div.find_all(['p', 'span', 'div', 'strong', 'em']):
                    child['contenteditable'] = 'true'

            html_output = str(soup)

        except Exception as e:
            print(f"❌ ftml 解析失败: {e}")
            html_output = _fallback_basic_parse(text)
    else:
        html_output = _fallback_basic_parse(text)

    # ========================================================
    # 阶段 4：占位符与金库还原
    # ========================================================
    if store:
        # 修复：倒序还原组件。
        # 在嵌套情况下，外层组件（如 Document 框）晚于内层组件（如折叠块）注册。
        # 倒序遍历确保先还原外层组件，从而暴露出内部可能存在的内层组件占位符，接着内层占位符才能被后续遍历替换。
        items = list(store.get_all().items())
        for comp_uuid, comp in reversed(items):
            if comp['type'] == 'css-module':
                # 先让 ftml 原生解析，不进行基于 marker 的注入
                pass
            else:
                ph = f"WDKEY{comp_uuid}ENDWDKEY"
                html_output = html_output.replace(f"<p>{ph}</p>", comp['html'])
                html_output = html_output.replace(ph, comp['html'])

    for k in reversed(list(placeholders.keys())):
        html_output = html_output.replace(f"<p>{k}</p>", placeholders[k])
        html_output = html_output.replace(k, placeholders[k])

    # 【修复 1】：恢复 @@...@@ 原生标签
    html_output = html_output.replace(RAW_PROTECT_TOKEN_START, '@@')
    html_output = html_output.replace(RAW_PROTECT_TOKEN_END, '@@')
    
    # 【处理强制换行的空块 @@@@】
    # 1. 独立空行：如果它自己占了一行，就变成原生空段落 <p><br></p>，撑起可视高度，用户在编辑器里可以直接看到空行。
    html_output = html_output.replace(f"<p>{EMPTY_RAW_TOKEN}</p>", "<p><br></p>")
    html_output = html_output.replace(f"<div>{EMPTY_RAW_TOKEN}</div>", "<div><br></div>")
    # 2. 内联软换行：如果由于没有回车它被包在文本中间，ftml 本身就会用 <br> 夹住它（形成 <br>EMPTY_RAW_TOKEN<br>）。
    #    消除占位符后，自然变成纯正的 <br><br> 。这刚好对上了导出器里的换行导出逻辑！
    html_output = html_output.replace(EMPTY_RAW_TOKEN, "")

    return html_output


def _fallback_basic_parse(text: str) -> str:
    """极其基础的正则兜底 (防崩溃)"""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!:)//(.*?)//', r'<i>\1</i>', text)
    text = text.replace('\n', '<br>')
    return text