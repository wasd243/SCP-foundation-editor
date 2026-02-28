import re
from bs4 import BeautifulSoup, NavigableString

def rgb_to_hex(rgb_str):
    """将 rgb(r, g, b) 转换为 #RRGGBB，如果是 hex 则直接返回"""
    if not rgb_str: return ""
    rgb_str = rgb_str.strip()
    if rgb_str.startswith('#'): return rgb_str
    
    match = re.search(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', rgb_str)
    if match:
        r, g, b = map(int, match.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
    return rgb_str

def parse_node(node, state):
    """
    核心正向解析器 (已剥离 UI 和 self)
    将 HTML 节点递归转换为 Wikidot 语法
    """
    def safe_get(selector, attr='text'):
        el = node.select_one(selector)
        if not el: return ""
        if attr == 'text': return el.get_text().strip()
        return el.get(attr, "").strip()

    if isinstance(node, NavigableString): return str(node)

    # --- Advanced Wikidot [[table]] export ---
    if node.get('class') and 'wikidot-adv-table' in node.get('class', []):
        tbl_style = node.get('data-wd-style', '')
        tbl_style_part = f' style="{tbl_style}"' if tbl_style else ''
        lines = [f'[[table{tbl_style_part}]]']
        all_rows = []
        for child in node.children:
            if hasattr(child, 'name'):
                if child.name == 'tr':
                    all_rows.append(child)
                elif child.name in ['tbody', 'thead', 'tfoot']:
                    all_rows.extend(child.find_all('tr', recursive=False))
        for tr in all_rows:
            row_style = tr.get('data-wd-style', '')
            row_style_part = f' style="{row_style}"' if row_style else ''
            lines.append(f'[[row{row_style_part}]]')
            for cell in tr.find_all(['td', 'th'], recursive=False):
                cell_style = cell.get('data-wd-style', '')
                cell_style_part = f' style="{cell_style}"' if cell_style else ''
                inner = ''.join(parse_node(c, state) for c in cell.contents).strip()
                lines.append(f'[[cell{cell_style_part}]]')
                if inner: lines.append(inner)
                lines.append('[[/cell]]')
            lines.append('[[/row]]')
        lines.append('[[/table]]')
        return '\n' + '\n'.join(lines) + '\n'

    if node.name == 'table':
        lines = []
        all_rows = []
        for child in node.children:
            if child.name == 'tr':
                all_rows.append(child)
            elif child.name in ['tbody', 'thead', 'tfoot']:
                all_rows.extend(child.find_all('tr', recursive=False))

        for tr in all_rows:
            line_parts = []
            for cell in tr.find_all(['td', 'th'], recursive=False):
                colspan = int(cell.get('colspan', '1'))
                prefix = "||" * colspan
                content = "".join(parse_node(c, state) for c in cell.contents).strip()
                content = content.replace('\n', ' _\n')
                if cell.name == 'th': prefix += "~ "
                else: prefix += " "
                line_parts.append(f"{prefix}{content}")
            lines.append(" ".join(line_parts) + " ||")
        return "\n" + "\n".join(lines) + "\n"

    if node.get('class') and 'scp-component' in node.get('class'):
        c_type = node.get('data-type')

        if c_type == 'theme-basalt': return ""

        if c_type == 'aim':
            f = lambda d: safe_get(f'[data-field="{d}"]')
            blocks = node.get('data-blocks', '')
            code = "[[include :scp-wiki-cn:component:advanced-information-methodology\n"
            if blocks: code += f"|blocks={blocks}\n"
            code += "|lang=CN\n"
            if blocks != '!': code += f"|XXXX={f('xxxx')}\n|lv={f('lv')}\n|cc={f('cc')}\n|dc={f('dc')}\n"
            if blocks != '-': code += f"|site={f('site')}\n|dir={f('dir')}\n|head={f('head')}\n|mtf={f('mtf')}\n"
            code += "]]\n"
            return code

        if c_type == 'html5player':
            url = safe_get('.html5player-url', 'text')
            return f"[[include :snippets:html5player\n|type=audio\n|url={url}]]\n"

        if c_type == 'foundation-bg':
            title_node = node.select_one('.foundation-title h1')
            desc_h1_node = node.select_one('.foundation-desc h1')
            desc_p_node = node.select_one('.foundation-desc p')
            item_node = node.select_one('.foundation-itemno h1')
            
            title_text = "".join(parse_node(c, state) for c in title_node.contents).strip() if title_node else "标题"
            desc_h1_text = "".join(parse_node(c, state) for c in desc_h1_node.contents).strip() if desc_h1_node else "副标题"
            desc_p_text = "".join(parse_node(c, state) for c in desc_p_node.contents).strip() if desc_p_node else "描述 " * 60
            item_text = "".join(parse_node(c, state) for c in item_node.contents).strip() if item_node else "XXXX"
            
            title_text = re.sub(r'[\n\r]+', '', title_text).replace('@@@@', '').replace('@@ @@', '').strip()
            desc_h1_text = re.sub(r'[\n\r]+', '', desc_h1_text).replace('@@@@', '').replace('@@ @@', '').strip()
            desc_p_text = re.sub(r'[\n\r]+', '', desc_p_text).replace('@@@@', '').replace('@@ @@', '').strip()
            item_text = re.sub(r'[\n\r]+', '', item_text).replace('@@@@', '').replace('@@ @@', '').strip()
            
            css = "[[module CSS]]\n.orderwrapper {position: relative;width: auto;text-align: center;}.council1 {position: relative;top: 0;bottom: 0;left: 0;right: 0;width: 295px;height: 295px;margin: auto;background-image: url( \"http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png\" );background-size: 295px 295px;background-repeat: no-repeat;background-position: center;}.ordertitle {position: absolute;left: 0;right: 0;top: 38px;}.ordertitle h1 {font-size: 220%;color: #555;}.orderdescription {position: absolute;left: 0;right: 0;top: 85px;width: 100%;}.orderdescription p {font-size: 90%;color: #555;}.orderdescription h1 {font-size: 120%;color: #555;}.itemno {position: absolute;left: 0;right: 0;bottom: 27px;}.itemno h1 {font-size: 170%;color: #555;}\n[[/module]]"
            
            res = f"[[div class=\"orderwrapper\"]]\n[[div class=\"council1\"]]\n[[/div]]\n[[div class=\"ordertitle\"]]\n+* {title_text}\n[[/div]]\n[[div class=\"orderdescription\"]]\n _\n+* {desc_h1_text}\n{desc_p_text}\n[[/div]]\n[[div class=\"itemno\"]]\n+* {item_text}\n[[/div]]\n[[/div]]\n\n{css}\n"
            return f"\n{res}\n"

        if c_type == 'image-block':
            name = safe_get('[data-field="name"]')
            caption = safe_get('[data-field="caption"]')
            align = node.get('data-align', 'right')
            return f"\n[[include component:image-block name={name}\n|caption={caption}\n|align={align}]]\n"

        if c_type == 'image-block-adv':
            name = safe_get('[data-field="name"]')
            caption = safe_get('[data-field="caption"]')
            width = safe_get('[data-field="width"]')
            height = safe_get('[data-field="height"]')
            align = node.get('data-align', 'right')

            res = f"\n[[include component:image-block\n|name={name}\n|caption={caption}"
            if width:
                width_val = width.lower().strip()
                if width_val and not (width_val.endswith('px') or width_val.endswith('%')): width_val += "px"
                res += f"\n|width={width_val}"
            if height:
                height_val = height.lower().strip()
                if height_val and not (height_val.endswith('px') or height_val.endswith('%')): height_val += "px"
                res += f"\n|height={height_val}"
            res += f"\n|align={align}]]\n"
            return res

        if c_type == 'tabview':
            buttons = node.select('.tab-header .tab-btn')
            contents = node.select('.tab-contents .tab-item')
            code = "\n[[tabview]]\n"
            for i, btn in enumerate(buttons):
                title = btn.get_text().strip()
                if i < len(contents):
                    tab_body = "".join(parse_node(c, state) for c in contents[i].contents).strip()
                    code += f"[[tab {title}]]\n{tab_body}\n[[/tab]]\n"
            code += "[[/tabview]]\n"
            return code

        if c_type == 'user': return f"[[*user {safe_get('.user-name')}]]"
        if c_type == 'user-adv': return f"[[*user {safe_get('.user-name')}]]"

        if c_type == 'email-example':
            show_title = node.select_one('.email-show-title').get_text(strip=True) if node.select_one('.email-show-title') else "访问SCiPNET邮件？一 (1) 封新邮件！"
            hide_title = node.select_one('.email-hide-title').get_text(strip=True) if node.select_one('.email-hide-title') else "回复：主题"
            to1 = node.select_one('.email-to1').get_text(strip=True) if node.select_one('.email-to1') else "收件人"
            from1 = node.select_one('.email-from1').get_text(strip=True) if node.select_one('.email-from1') else "发件人"
            subj1 = node.select_one('.email-subj1').get_text(strip=True) if node.select_one('.email-subj1') else "主题"
            c1_node = node.select_one('.email-content1')
            cont1 = "".join(parse_node(c, state) for c in c1_node.contents).strip() if c1_node else "文本"

            to2 = node.select_one('.email-to2').get_text(strip=True) if node.select_one('.email-to2') else "收件人"
            from2 = node.select_one('.email-from2').get_text(strip=True) if node.select_one('.email-from2') else "发件人"
            subj2 = node.select_one('.email-subj2').get_text(strip=True) if node.select_one('.email-subj2') else "回复：主题"
            c2_node = node.select_one('.email-content2')
            cont2 = "".join(parse_node(c, state) for c in c2_node.contents).strip() if c2_node else "文本"

            return f'\n[[div class="email-example"]]\n[[=]]\n------\n[[collapsible show="{show_title}" hide="{hide_title}"]]\n[[<]]\n[[div class="email"]]\n[[div class="tofrom"]]\n**至：**{to1}\n**自：**{from1}\n**主题：**{subj1}\n[[/div]]\n------\n{cont1}\n[[/div]]\n@@ @@\n[[div class="email"]]\n[[div class="tofrom"]]\n**至：**{to2}\n**自：**{from2}\n**主题：**{subj2}\n[[/div]]\n------\n{cont2}\n[[/div]]\n[[/<]]\n[[/collapsible]]\n[[/=]]\n[[/div]]\n'

        if c_type == 'collapsible':
            show_t = safe_get('[data-field="show"]')
            hide_t = safe_get('[data-field="hide"]')
            inner = "".join(parse_node(c, state) for c in node.select_one('.collapsible-content-area').contents)
            return f'\n[[collapsible show="{show_t}" hide="{hide_t}"]]\n{inner.strip()}\n[[/collapsible]]\n'

        if c_type == 'license': return ""

        if c_type == 'acs':
            item = safe_get('[data-field="item-number"]')
            clr = (re.search(r'\d+', safe_get('[data-field="clearance"]')) or re.search(r'\d+', '1')).group()
            sec = safe_get('[data-field="secondary"]').lower()
            if sec == "none": sec = ""
            cnt = '机密' if sec else safe_get('[data-field="container"]').lower()
            dsr = safe_get('[data-field="disruption"]').lower()
            rsk = safe_get('[data-field="risk"]').lower()

            anim = ""
            if node.select_one('.acs-anim-checkbox') and node.select_one('.acs-anim-checkbox').has_attr('checked'):
                anim = "[[include :scp-wiki-cn:component:acs-animation]]\n"

            sec_line = ""
            if sec:
                sec_line = f"|secondary-class={sec}\n"
                sec_icon = safe_get('[data-field="secondary-icon"]')
                if sec_icon: sec_line += f"|secondary-icon={sec_icon}\n"

            res = f"[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number={item}\n|clearance={clr}\n|container-class={cnt}\n{sec_line}|disruption-class={dsr}\n|risk-class={rsk}\n]]"
            
            if node.select_one('.acs-shiver-checkbox') and node.select_one('.acs-shiver-checkbox').has_attr('checked'):
                res = f'[[div class="Shivering-ACS"]]\n{res}\n[[/div]]'
            return f"\n{anim}{res}\n"

        if c_type == 'toc': return "\n[[toc]]\n"

        if c_type == 'footnote':
            content = node.get('data-content', '').strip()
            if state.get('better_footnotes', False):
                return f'[[span class="fnnum"]].[[/span]][[span class="fncon"]]{content}[[/span]]'
            else:
                return f"[[footnote]] {content} [[/footnote]]"

        if c_type == 'hr': return "\n------\n"

        if c_type == 'raisa-notice':
            style = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5;"
            inner = "".join(parse_node(c, state) for c in node.select_one('.raisa-content').contents).strip()
            return f"\n[[div style=\"{style}\"]]\n{inner}\n[[/div]]\n"

        if c_type == 'class-warning':
            style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) bottom right no-repeat; border: solid 2px black; padding: 0 20px 20px 20px; margin: 10px auto; width: fit-content; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"
            inner = "".join(parse_node(c, state) for c in node.select_one('.class-warning-content > .class-warning-inner').contents)
            inner = re.sub(r'[\n\r]+', '', inner).replace('@@@@', '').replace('@@ @@', '')
            return f"\n[[=]]\n[[div style=\"{style}\"]]\n{inner}\n[[/div]]\n[[/=]]\n"

        if c_type == 'o5-command':
            style = "background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px;"
            h2_node = node.select_one('.o5-h2')
            p_node = node.select_one('.o5-p')
            h1_node = node.select_one('.o5-h1')
            
            part1 = "".join(parse_node(c, state) for c in h2_node.contents) if h2_node else ""
            part2 = "".join(parse_node(c, state) for c in p_node.contents) if p_node else ""
            part3 = "".join(parse_node(c, state) for c in h1_node.contents) if h1_node else ""
            
            part1 = re.sub(r'[\n\r]+', '', part1).replace('@@@@', '').replace('@@ @@', '').strip()
            part2 = re.sub(r'[\n\r]+', '', part2).replace('@@@@', '').replace('@@ @@', '').strip()
            part3 = re.sub(r'[\n\r]+', '', part3).replace('@@@@', '').replace('@@ @@', '').strip()
            
            res = f"\n[[div style=\"{style}\"]]\n@@@@\n@@@@\n@@@@\n@@@@\n[[=]]\n"
            if part1: res += f"++* {part1}\n"
            if part2: res += f"{part2}\n"
            res += "[[/=]]\n"
            if part3: res += f"= {part3}\n"
            res += "@@@@\n@@@@\n[[/div]]\n"
            return res

        if c_type == 'page-note':
            PAGE_CSS = '[[module CSS]]\n.page {\n    display: block;\n    overflow: hidden;\n    font-family: "Monotype Corsiva", "Bradley Hand ITC", sans-serif;\n    font-style: normal;\n\n    background-attachment: scroll;\n    background-clip: border-box;\n    background-color: transparent;\n    background-image: linear-gradient(to top ,rgb(202, 219, 228) 0%, rgb(231, 233, 220) 8%);\n    background-origin: padding-box;\n    background-position: 0px 8px;\n    background-repeat: repeat;\n    background-size: 100% 20px;\n\n    border: 1px solid #CCC;\n    border-radius: 10px;\n    padding: 10px 10px;\n    margin-bottom: 10px;\n\n    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.2)\n    }\n.page p,\n.page ul {\n    line-height: 20px;\n    margin: 0;\n}\n[[/module]]'
            content_node = node.select_one('.page-note-content')
            inner = ''.join(parse_node(c, state) for c in content_node.contents).strip() if content_node else ''
            return f"\n{PAGE_CSS}\n[[div class=\"page\"]]\n{inner}\n[[/div]]\n"

        if c_type == 'login-logout':
            FAKEPROT_CSS = '[[module CSS]]\n.fakeprot .mailform-box .buttons{display:none;}\n.fakeprot + .collapsible-block .collapsible-block-link {padding: 0.1em 0.5em;text-decoration: none;background-color: #F4F4F4;border: 1px solid #AAA;color: #000;}\n.fakeprot + .collapsible-block .collapsible-block-link:hover {background-color: #DDD;color: #000;}\n.fakeprot + .collapsible-block .collapsible-block-link:active {background-color: #DDD;color: #000;}\n.fakeprot + .collapsible-block .collapsible-block-unfolded-link{margin:0.5em 0;text-align: center;}\n.fakeprot + .collapsible-block .collapsible-block-folded{margin:0.5em 0;text-align: center;}\n.fakeprot .passw input[type=text] {text-security:disc;-webkit-text-security:disc;-mox-text-security:disc;}\n.mailform-box td:first-child {width: 80px;}\n[[/module]]'
            id_val_node = node.select_one('.login-id-value')
            id_val = id_val_node.get_text().strip() if id_val_node else '你的ID'
            coll_node = node.select_one('.login-collapsible-content')
            coll_inner = ''.join(parse_node(c, state) for c in coll_node.contents).strip() if coll_node else '文字'
            fakeprot_block = f'[[div class="fakeprot"]]\n[[module MailForm to="aaaa (DUMMY)" button=""]]\n# name\n * title: ID\n * default: <{id_val}>\n * type: text\n * rules:\n  * required: true\n  * maxLength:10\n  * minLength: 100\n[[/module]]\n[[div class="passw"]]\n[[module MailForm to="aaaa (DUMMY)" button=""]]\n# affiliation\n * title: 密码\n * default: ・・・・・・・・・\n * rules:\n  * required: true\n  * maxLength:10\n  * minLength: 100\n[[/module]]\n[[/div]]\n[[/div]]\n[[collapsible show="登入" hide="登出"]]\n{coll_inner}\n[[/collapsible]]'
            return f'\n{FAKEPROT_CSS}\n{fakeprot_block}\n'

        if c_type == 'div-block':
            params = safe_get('.div-header', 'text').replace('DIV:', '').strip()
            if params.startswith('[[div') and params.endswith(']]'):
                params = params[5:-2].strip()
            inner = "".join(parse_node(c, state) for c in node.select_one('.div-content').contents).strip()
            return f"\n[[div {params}]]\n{inner}\n[[/div]]\n"

        if c_type == 'css-module':
            css_code = safe_get('.css-content', 'text').strip()
            return f"\n[[module CSS]]\n{css_code}\n[[/module]]\n"

    tag = node.name
    inner_state = state
    if tag in ['b', 'strong']:
        if state.get('in_bold'): return "".join(parse_node(child, state) for child in node.contents)
        inner_state = state.copy()
        inner_state['in_bold'] = True
    elif tag in ['i', 'em']:
        if state.get('in_italic'): return "".join(parse_node(child, state) for child in node.contents)
        inner_state = state.copy()
        inner_state['in_italic'] = True

    content = "".join(parse_node(child, inner_state) for child in node.contents)
    content = content.replace('\u200b', '')

    if tag == 'p':
        if 'forced-break' in node.get('class', []):
            source = node.get('data-source', '@@@@')
            return f"\n{source}\n"
        def expand_soft_breaks(match):
            count = len(match.group(0))
            return "\n" + ("@@@@\n" * (count - 1))
        content = re.sub(r'\n{2,}', expand_soft_breaks, content)
        clean = content.replace('**', '').replace('//', '').replace('__', '').replace('^^', '').replace(',,', '').strip()
        if not clean: return "\n@@@@\n"
    
    if tag == 'br': return "\n"

    style = node.get('style', '') if hasattr(node, 'get') else ''
    align_mark = ""
    if 'text-align: right' in style or 'text-align:right' in style: align_mark = ">"
    elif 'text-align: left' in style or 'text-align:left' in style: align_mark = "<"
    elif 'text-align: center' in style or 'text-align:center' in style: align_mark = "="

    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(tag[1])
        return f"\n{'+' * level} {content.strip()}\n"

    if tag == 'span' and 'custom-dash' in node.get('class', []):
        try: count = int(node.get('data-count', '6'))
        except ValueError: count = 6
        return f'@{"-" * count}@'

    if tag == 'span' and node.has_attr('style'):
        if not content.strip(): return content
        if 'monospace' in style or 'Courier' in style: return f"{{{{{content}}}}}"
        res = content
        color_match = re.search(r'color:\s*([^;]+)', style)
        if color_match:
            color_val = rgb_to_hex(color_match.group(1).strip())
            res = f"###{color_val[1:]}|{res}##" if color_val.startswith('#') else f"##{color_val}|{res}##"
        size_match = re.search(r'font-size:\s*([\w\.\-%]+)', style)
        if size_match: res = f"[[size {size_match.group(1).strip()}]]{res}[[/size]]"
        if 'underline' in style:
            match = re.fullmatch(r'(\s*)(.*?)(\s*)', res, flags=re.DOTALL)
            if match and match.group(2): res = f"{match.group(1)}__{match.group(2)}__{match.group(3)}"
        if 'line-through' in style:
            match = re.fullmatch(r'(\s*)(.*?)(\s*)', res, flags=re.DOTALL)
            if match and match.group(2): res = f"{match.group(1)}--{match.group(2)}--{match.group(3)}"
        return res

    if tag == 'font':
        if not content.strip(): return content
        res = content
        if node.has_attr('color'): res = f"##{node['color']}|{res}##"
        return res

    if tag == 'sup': 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)}^^{match.group(2)}^^{match.group(3)}"
        return content
    if tag == 'sub': 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)},,{match.group(2)},,{match.group(3)}"
        return content
    if tag == 'u': 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)}__{match.group(2)}__{match.group(3)}"
        return content
    if tag in ['s', 'strike', 'del']: 
        match = re.fullmatch(r'(\s*)(.*?)(\s*)', content, flags=re.DOTALL)
        if match and match.group(2): return f"{match.group(1)}--{match.group(2)}--{match.group(3)}"
        return content

    if tag == 'li':
        parent = node.parent
        return f"* {content.strip()}\n" if parent.name == 'ul' else f"# {content.strip()}\n"

    if tag == 'blockquote':
        lines = content.split('\n')
        return "".join(f"> {line}\n" for line in lines) + "\n"

    if tag == 'a':
        href = node.get('href')
        prefix = "*" if node.get('target') == '_blank' else ""
        return f"[{prefix}{href} {content.strip()}]"

    if tag == 'p':
        val = f"{content}\n"
        if align_mark: return f"[[{align_mark}]]\n{content.strip()}\n[[/{align_mark}]]\n"
        return val

    if tag == 'div':
        if align_mark: return f"[[{align_mark}]]\n{content.strip()}\n[[/{align_mark}]]\n"
        if node.has_attr('class'):
            cls = " ".join(node['class'])
            exclude_list = ['scp-component', 'div-content', 'div-header', 'basalt-theme', 'bhl-theme', 'shivering-theme']
            if not any(x in cls for x in exclude_list):
                return f"[[div class=\"{cls}\"]]\n{content}\n[[/div]]\n"
            else:
                return content
        clean = content.replace('**', '').replace('//', '').replace('__', '').replace('^^', '').replace(',,', '').strip()
        if not clean: return "\n@@@@\n"
        def expand_soft_breaks(match):
            return "\n" + ("@@@@\n" * (len(match.group(0)) - 1))
        content_fixed = re.sub(r'\n{2,}', expand_soft_breaks, content)
        return f"{content_fixed}\n"

    if tag in ['b', 'strong']: return f"**{content}**" if content.strip() else content
    if tag in ['i', 'em']: return f"//{content}//" if content.strip() else content
    return content

def export_html_to_wikidot(html: str, snapshot: dict) -> str:
    """
    外部主入口：将包含编辑器界面的 HTML 以及当前的状态快照，转换为纯 Wikidot 代码。
    """
    soup = BeautifulSoup(html, 'html.parser')
    root = soup.find(id="editor-root")
    if not root: return ""

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
        
    if soup.select_one('.email-example-box'):
         final_code += "[[module CSS]]\n.email-example .collapsible-block-folded a.collapsible-block-link {\n    animation: blink 0.8s ease-in-out infinite alternate;\n}\n@keyframes blink {\n    0% { color: transparent; }\n    50%, 100% { color: #b01; }\n}\n.email {border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.5)}\n.email-example a.collapsible-block-link {font-weight: bold;}\n.tofrom {margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon}\n[[/module]]\n"

    parse_state = {'better_footnotes': use_better_footnotes}

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

    body_parts = []
    for c in root.contents:
        if isinstance(c, NavigableString):
            if not str(c).strip(): continue
        body_parts.append(parse_node(c, parse_state))
    
    raw_body = "".join(body_parts)

    body = raw_body.replace('\r\n', '\n').replace('\xa0', ' ')
    body = re.sub(r'\n[ \t]*\n[ \t]*(@@@@|@@ @@)', r'\n\1', body)
    body = re.sub(r'(@@@@|@@ @@)\n\s*\n+', r'\1\n', body)
    body = re.sub(r'([^\n])\s*(\[\[include component:image-block)', r'\1\n\2', body)
    body = re.sub(r'^[ \t]+(\[\[include component:image-block)', r'\1', body, flags=re.MULTILINE)

    final_code += body
    final_code += license_code
    
    return final_code