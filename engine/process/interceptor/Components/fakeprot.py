import re

def process_fakeprot(text: str, store, inner_parser_cb, theme_type: str) -> str:
    """
    拦截包裹嵌套渲染 [[div class="fakeprot"]] 和 [[collapsible]] 盒子的逻辑系统。
    这部分 ftml 原生解析较弱，因而手动拦截以模拟完整登入界面骨架。
    """
    result = []
    cursor = 0
    txt = text
    pat_div_start = re.compile(r'\[\[div\s+class=["\']fakeprot["\']\]\]', re.IGNORECASE)
    pat_div_close = re.compile(r'\[\[/div\]\]', re.IGNORECASE)
    pat_coll = re.compile(r'\s*\[\[collapsible\s+show="([^"]*)"\s+hide="([^"]*)"\]\](.*?)\[\[/collapsible\]\]', re.DOTALL | re.IGNORECASE)

    for m_start in pat_div_start.finditer(txt):
        div_start = m_start.start()
        if div_start < cursor: continue
        
        depth = 1
        i = m_start.end()
        div_end = None
        
        while i < len(txt) and depth > 0:
            next_open = re.search(r'\[\[div', txt[i:], re.IGNORECASE)
            next_close = pat_div_close.search(txt[i:])
            if not next_close: break
            
            pos_close = i + next_close.start()
            pos_open = i + next_open.start() if next_open else -1
            
            if next_open and pos_open < pos_close:
                depth += 1
                i = pos_open + 5
            else:
                depth -= 1
                i = pos_close + 8
                if depth == 0: div_end = i
                
        if div_end is None: continue

        inner_content = txt[m_start.end(): div_end - 8]
        coll_m = pat_coll.match(txt, div_end)
        
        if coll_m:
            coll_content_raw = coll_m.group(3)
            block_end = coll_m.end()
        else:
            coll_content_raw = '文字'
            block_end = div_end

        id_dm = re.search(r'\*\s*default:\s*<([^>]+)>', inner_content)
        id_val = id_dm.group(1).strip() if id_dm else '你的ID'

        parsed_coll = inner_parser_cb(coll_content_raw.strip(), theme_type)

        ll_html = (
            '<div class="scp-component login-logout-box" data-type="login-logout" data-source-uuid="{{uuid}}" data-source="{{source}}" contenteditable="false" style="border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;">'
            '<table class="login-form-table" contenteditable="false" style="margin:0.5em auto; border-collapse:collapse;"><tr>'
            '<td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">ID</td>'
            f'<td><span class="login-id-value" contenteditable="true" data-field="id" style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;">{id_val}</span></td></tr>'
            '<tr><td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">密码</td>'
            '<td><span contenteditable="false" style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif; color:#555; letter-spacing:2px;">・・・・・・・・・</span></td></tr>'
            '<tr><td contenteditable="false"></td><td style="text-align:center;" contenteditable="false"><button contenteditable="false" style="padding:2px 18px; border:1px solid #aaa; background:#f4f4f4;  font-family:sans-serif;">登入</button></td></tr></table>'
            '<hr contenteditable="false" style="border:none; border-top:1px solid #ccc; margin:6px 0;">'
            '<div contenteditable="false" style="font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;">[登入]↔[登出] 折叠内容</div>'
            f'<div class="login-collapsible-content" contenteditable="true" style="min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;">{parsed_coll}</div></div>'
        )
        
        source = txt[div_start:block_end]
        result.append(txt[cursor:div_start])
        result.append(store.register_html(source, "login-logout", ll_html))
        cursor = block_end

    result.append(txt[cursor:])
    return ''.join(result)
