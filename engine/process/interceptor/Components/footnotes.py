import re
import html as _html_module

def process_footnotes(text: str, store) -> str:
    """
    处理 Wikidot 脚注 (标准和 BetterFootnotes)
    将其转换为带有 data-content 的小角标 span 元素，然后存入 store 避免被 ftml 引擎修改。
    前方 UI 的 JS 脚本 (footnotes.js) 会在载入结束后以及每次输入时重新遍历所有角标赋予编号 1,2,3...
    """
    processed_text = text

    # ==========================
    # 1. 拦截基础 Wikidot 脚注
    # 语法: [[footnote]]内容[[/footnote]]
    # ==========================
    def fn_replacer(match):
        source = match.group(0)
        content = match.group(1)
        # 这里默认渲染 #, 前端 JS 的 refreshFootnotes() 会随后把它替换成数字 1, 2, 3...
        html = f'<span class="scp-component scp-footnote" data-type="footnote" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-content="{_html_module.escape(content)}" title="{_html_module.escape(content)}" contenteditable="false">#</span>'
        return store.register_html(source, "footnote", html)
        
    processed_text = re.sub(r'\[\[footnote\]\](.*?)\[\[/footnote\]\]', fn_replacer, processed_text, flags=re.DOTALL)

    # ==========================
    # 2. 拦截中分常用组件 Better Footnotes
    # 语法: [[span class="fnnum"]].[[/span]][[span class="fncon"]]内容[[/span]]
    # ==========================
    def bf_replacer(match):
        source = match.group(0)
        content = match.group(2).strip()
        html = f'<span class="scp-component scp-footnote" data-type="footnote" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-content="{_html_module.escape(content)}" title="{_html_module.escape(content)}" contenteditable="false">#</span>'
        return store.register_html(source, "footnote", html)
        
    processed_text = re.sub(r'\[\[span\s+class=["\']fnnum["\']\]\](.*?)\[\[/span\]\]\[\[span\s+class=["\']fncon["\']\]\](.*?)\[\[/span\]\]', bf_replacer, processed_text, flags=re.DOTALL)

    return processed_text
