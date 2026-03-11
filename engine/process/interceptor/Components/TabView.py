import re

def process_tabview(text: str, store, inner_parser_cb, theme_type: str) -> str:
    """
    处理选项卡组件 (TabView)
    将 [[tabview]] 语法解析为可编辑的并携带切换行为（TabView.js）的选项卡布局 HTML 结构。
    """
    processed_text = text

    def tabview_replacer(match):
        source = match.group(0)
        content = match.group(1)
        tabs = re.findall(r'\[\[tab ([^\]]+)\]\](.*?)\[\[/tab\]\]', content, flags=re.DOTALL)
        
        header_html, body_html = "", ""
        for i, (title, body) in enumerate(tabs):
            active = " active" if i == 0 else ""
            header_html += f'<span class="tab-btn{active}" contenteditable="true" onclick="selectTab(this)">{title.strip()}</span>'
            body_html += f'<div class="tab-item{active}" contenteditable="true">{inner_parser_cb(body, theme_type)}</div>'
            
        html = f'''<div class="scp-component tabview-box" data-type="tabview" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false"><div class="tab-header">{header_html}<span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents">{body_html}</div></div>'''
        
        return store.register_html(source, "tabview", html)

    processed_text = re.sub(r'\[\[tabview\]\](.*?)\[\[/tabview\]\]', tabview_replacer, processed_text, flags=re.DOTALL)
    
    return processed_text
