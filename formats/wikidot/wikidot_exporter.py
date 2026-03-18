import re
from bs4 import BeautifulSoup, NavigableString
# import rgb_to_hex
from formats.wikidot.rgb.rgb_to_hex import handle_rgb_to_hex

def rgb_to_hex(rgb_str):
    """ turn rgb color into format like #000000"""
    return handle_rgb_to_hex(rgb_str)

try:
    # import parse_node
    from formats.wikidot.parse_node.parse_node import handle_parse_node
    def parse_node(node, state):
        """ parse node into wikidot code"""
        return handle_parse_node(node, state)
except ImportError:
    def parse_node(node, state):
        """ parse node into wikidot code"""
        return ""

def export_html_to_wikidot(html: str, snapshot: dict) -> str:
    """
    外部主入口：将包含编辑器界面的 HTML 以及当前的快照状态，转换为纯 Wikidot 代码。
    
    :param html: 从编辑器传入的完整 HTML DOM 代码
    :param snapshot: 当前界面的勾选框/主题状态 (如 basalt_on)
    :return: 干净可用的 Wikidot 语法文本
    """
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.find(id="editor-root")
    if not root: return ""
    
    # 提取所有 <style> 标签 (不论在 head 还是 body)，稍后在前面统一输出 (置顶 CSS 导出)
    head_styles_code = ""
    seen_css_blocks = set()
    for style_tag in soup.find_all('style'):
        # 跳过 data-no-hoist（如基金会背景，它的CSS应跟在组件后面）
        if style_tag.get('data-no-hoist') == 'true':
            continue
        parsed = parse_node(style_tag, {})
        # 过滤重复、空块及 rate-module 误读
        css_content = parsed.strip() if parsed else ''
        if css_content and css_content not in seen_css_blocks and '[[module Rate]]' not in css_content:
            seen_css_blocks.add(css_content)
            head_styles_code += css_content + "\n"
        # 删除节点，防止稍后在 body 遍历中被重复导出
        style_tag.decompose()


    # ==========================================
    # 步骤 1：梳理页面顶部级的组件 (Rate、主题CSS等)
    # 根据页面的 snapshot 的全局设定，决定页面最上方插入哪些 Wikidot 组件或内联配置
    # ==========================================

    rate_box = soup.select_one('.rate-module-box')
    rate_code = ""
    if rate_box:
        is_hidden = rate_box.get('data-hidden') == 'true'
        if not is_hidden:
            align = rate_box.get('data-align', '')
            if align == 'left': rate_code = "[[<]]\n[[module Rate]]\n[[/<]]\n"
            elif align == 'right': rate_code = "[[>]]\n[[module Rate]]\n[[/>]]\n"
            else: rate_code = "[[module Rate]]\n"
        rate_box.decompose() 

    use_better_footnotes = snapshot.get('bf_on', False)

    theme_code = ""
    if snapshot.get('basalt_on'):
        opts = []
        if snapshot.get('basalt_dark'): opts.append('darkmode=a')
        if snapshot.get('basalt_wide'): opts.append('wide=a')
        if snapshot.get('basalt_hide'): opts.append('hidetitle=a')
        if opts: theme_code += '[[include :scp-wiki-cn:theme:basalt 版式设置|' + '|'.join(opts) + ']]\n'
        else: theme_code += '[[include :scp-wiki-cn:theme:basalt]]\n'
    elif snapshot.get('shiver_on'):
        suffix = ''
        if snapshot.get('shiv_mo'):   suffix = ' mo=*'
        elif snapshot.get('shiv_kl'): suffix = ' kl=*'
        elif snapshot.get('shiv_dub'): suffix = ' dub=*'
        elif snapshot.get('shiv_ct'):  suffix = ' ct=*'
        elif snapshot.get('shiv_ba'):  suffix = ' ba=*'
        theme_code += f'[[include :scp-wiki-cn:theme:shivering-night{suffix}]]\n'
    elif snapshot.get('bhl_on'):
        theme_code += '[[include :scp-wiki-cn:theme:black-highlighter-theme]]\n'
        if snapshot.get('bhl_sidebar'):  theme_code += '[[include :scp-wiki:component:bhl-dark-sidebar]]\n'
        if snapshot.get('bhl_coll'):     theme_code += '[[include :scp-wiki:component:collapsible-sidebar]]\n'
        if snapshot.get('bhl_toggle'):   theme_code += '[[include :scp-wiki:component:toggle-sidebar-bhl]]\n'
        if snapshot.get('bhl_center'):   theme_code += '[[include :scp-wiki:component:centered-header-bhl]]\n'
        if snapshot.get('bhl_office'):   theme_code += '[[include :scp-wiki-cn:theme:scp-offices-theme]]\n'

    final_code = theme_code + rate_code
    if use_better_footnotes: final_code += "[[include :scp-wiki-cn:component:betterfootnotes]]\n"
        
    # TOC 功能：检测是否需要插入 [[toc]]
    # 如果任意标题带有 data-toc-anchor 属性，且当前代码中尚未包含 [[toc]]
    if 'data-toc-anchor' in html and '[[toc]]' not in final_code:
        final_code += "[[toc]]\n"

    if soup.select_one('.email-example-box'):
        # email-example-box 的专属 CSS 直接注入 head_styles_code（已有去重逻辑）
        email_css_block = (
            "[[module CSS]]\n"
            ".email-example .collapsible-block-folded a.collapsible-block-link {\n"
            "    animation: blink 0.8s ease-in-out infinite alternate;\n"
            "}\n"
            "@keyframes blink {\n"
            "    0% { color: transparent; }\n"
            "    50%, 100% { color: #b01; }\n"
            "}\n"
            ".email {border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.5)}\n"
            ".email-example a.collapsible-block-link {font-weight: bold;}\n"
            ".tofrom {margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon}\n"
            "[[/module]]\n"
        )
        key = email_css_block.strip()
        if key not in seen_css_blocks:
            seen_css_blocks.add(key)
            head_styles_code += email_css_block

    parse_state = {
        'better_footnotes': use_better_footnotes,
        'mono_security': snapshot.get('mono_security_on', True),
        'line_break_symbol_lock': snapshot.get('line_break_symbol_lock_on', False)
    }

    def parse_license_only(comp_node):
        def get_field_lic(n, field):
            el = n.select_one(f'[data-field="{field}"]')
            return el.get_text().strip() if el else ""

        author = get_field_lic(comp_node, "author")
        translator = get_field_lic(comp_node, "translator")
        is_original = comp_node.get('data-original', 'false') == 'true'

        use_bf = parse_state.get('better_footnotes', False)
        fn_block = "" if use_bf else "[[footnoteblock]]\n"

        base_code = f"{fn_block}[[include :scp-wiki-cn:component:license-box\n"
        if is_original: base_code += "|lang=CN\n"
        if author: base_code += f"|author={author}\n"
        if not is_original and translator: base_code += f"|translator={translator}\n"
        base_code += "]]\n=====\n"

        files_code = ""
        file_entries = comp_node.select('.file-entry')
        for i, entry in enumerate(file_entries):
            fields = {
                '文件名': 'file_name', '图像名': 'img_name', '图像作者': 'img_author',
                '授权协议': 'img_license', '来源链接': 'source_link', '衍生自': 'derived_from', '备注': 'note'
            }
            has_any_field = False
            file_text = ""
            img_name_val = get_field_lic(entry, 'img_name')
            img_author_val = get_field_lic(entry, 'img_author')
            
            for label, key in fields.items():
                val = get_field_lic(entry, key)
                if val:
                    has_any_field = True
                    if key == 'img_author' and not img_name_val and img_author_val: label = '作者'
                    if label == '来源链接': file_text += f"> {label}：{val}\n"
                    else: file_text += f"> **{label}：**{val}\n"
            
            if has_any_field:
                files_code += file_text
                if i < len(file_entries) - 1: files_code += "\n"

        return base_code + files_code + "=====\n[[include :scp-wiki-cn:component:license-box-end]]\n"

    license_comps = root.find_all(attrs={"data-type": "license"})
    license_code = ""
    for comp in license_comps:
        license_code += parse_license_only(comp)
        comp.decompose()

    # ==========================================
    # 步骤 2：对主体节点进行依次递归遍历，调用 parse_node 转换为 Wikidot 语法
    # ==========================================
    body_parts = []
    for c in root.contents:
        if isinstance(c, NavigableString):
            if not str(c).strip(): continue
            
        parsed = parse_node(c, parse_state)
        
        # 修复：防止首行纯文本与随后的块级元素连在一起
        # 检查当前是否是块级元素，如果上一段内容的末尾没有换行符，且当前也不以换行符开头，则补齐换行符
        if getattr(c, 'name', '') in ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'blockquote', 'table']:
            if body_parts and not body_parts[-1].endswith('\n') and not parsed.startswith('\n'):
                parsed = '\n' + parsed
                
        body_parts.append(parsed)
    
    raw_body = "".join(body_parts)

    # ==========================================
    # 步骤 3：最终排版修正和换行符清理
    # ==========================================
    body = raw_body.replace('\r\n', '\n').replace('\xa0', ' ')

    # TOC：移除 body 中所有解析出来的 [[toc]]（因为会在顶部统一生成）
    body = re.sub(r'\[\[toc\]\]\s*', '', body, flags=re.IGNORECASE)

    body = re.sub(r'([^\n])\s*(\[\[include component:image-block)', r'\1\n\2', body)
    body = re.sub(r'^[ \t]+(\[\[include component:image-block)', r'\1', body, flags=re.MULTILINE)
    # 消除相邻 @@@@ 之间多余的空行（循环直到稳定，处理任意长度的连续序列）
    while '@@@@\n\n@@@@' in body:
        body = body.replace('@@@@\n\n@@@@', '@@@@\n@@@@')
    # 消除文本和 @@@@ 之间的空行
    body = re.sub(r'\n\n(@@@@)', r'\n\1', body)
    body = re.sub(r'(@@@@)\n\n', r'\1\n', body)
    # 消除所有靠左符号
    body = re.sub(r'\[\[<\]\]', '', body)
    body = re.sub(r'\[\[\/<\]\]', '', body)

    def remove_single_forced_break(match):
        between = match.group(2)
        if between.count('@@@@') <= 1:
            return f"{match.group(1)}\n{match.group(3)}"
        return match.group(0)

    # 针对两个文件模板相邻的情况，清除它们之间单独的强制换行符 (<=1)
    body = re.sub(
        r'(\[\[/div\]\])([\s@]+)(\[\[div\s+class=["\'](?:dark)?document.*?\]\])', 
        remove_single_forced_break, 
        body
    )

    # 针对重复嵌套/未清理干净的字号代码进行合并（如字号中套字号，只保留最外层配置，内容扁平化）
    # 比如：[[size xx-large]]测[[size xx-small]]试文[[/size]][[/size]] 应该变为 [[size xx-large]]测试文[[/size]]
    def flatten_sizes(text):
        # 此处使用简单的循环将内部嵌套的 size 提取并处理
        while True:
            # 找到内部包含 size 标签的外层 size 标签
            new_text = re.sub(
                r'(\[\[size\s+[^\]]+\]\])(.*?)\[\[size\s+[^\]]+\]\](.*?)\[\[/size\]\](.*?)(\[\[/size\]\])', 
                r'\1\2\3\4\5', 
                text, 
                flags=re.DOTALL | re.IGNORECASE
            )
            # 处理左侧相邻但前一标签覆盖至后一标签的内容残留 (例如：[[size small]]测[[/size]][[size xx-small]]试文[[/size]])
            # 如果两个相邻内容由于文本分离操作遗留了旧前缀。
            new_text = re.sub(
                r'\[\[size\s+[^\]]+\]\](.*?)\[\[/size\]\]\s*\[\[size\s+([^\]]+)\]\](.*?)\[\[/size\]\]',
                r'[[size \2]]\1\3[[/size]]',
                new_text,
                flags=re.DOTALL | re.IGNORECASE
            )
            if new_text == text:
                break
            text = new_text
        return text
    
    body = flatten_sizes(body)

    # 警告：之前这里的临时修复会清除用户正常指定的所有 [[size]] 标签，导致绝对字号无法生成
    # 现已将其注释，因为 clear_styles.js 已经在 DOM 层面直接移除了 style 属性
    # body = re.sub(r'\[\[size\s+[^\]]+\]\](.*?)\[\[/size\]\]', r'\1', body, flags=re.DOTALL | re.IGNORECASE)
    
    # 同理清除空的 ##color|...## 颜色标签（保留内容） - 仅清除明显是"无色"的标记
    # 注意：正常用户设置的颜色标签应保留，此处仅在已清除 style 情况下才会产生空标签
    body = re.sub(r'##(?:black|#000000|#000)\|([^#]*?)##', r'\1', body, flags=re.IGNORECASE)

    final_code += body
    final_code += license_code

    # 等宽字安全兜底：如果开启了安全模式，强制清除所有包含中文的等宽字标签 {{...}}
    if snapshot.get('mono_security_on', True):
        final_code = re.sub(r'\{\{([^{}]*[\u4e00-\u9fa5]+[^{}]*)\}\}', r'\1', final_code)

    combined = head_styles_code + final_code

    # ==========================================
    # 最终去重：保留每个 [[module CSS]] 块的独立性，
    # 但若内容已出现过（重复插入同一组件），则丢弃该块
    # ==========================================
    css_pattern = re.compile(
        r'\[\[module CSS\]\]\n?(.*?)\n?\[\[/module\]\]',
        re.DOTALL | re.IGNORECASE
    )
    seen_css_contents = set()

    def dedup_css_block(m):
        block = m.group(1).strip()
        if not block:
            return ''  # 空块直接丢弃
        if block in seen_css_contents:
            return ''  # 内容重复，丢弃
        seen_css_contents.add(block)
        return f"[[module CSS]]\n{block}\n[[/module]]"

    combined = css_pattern.sub(dedup_css_block, combined)

    # 清理多余的空行（连续三个以上换行压缩为两个）
    combined = re.sub(r'\n{3,}', '\n\n', combined).strip()

    return combined