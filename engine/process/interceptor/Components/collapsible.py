import re

def process_collapsible(text: str, store, inner_parser_cb, theme_type: str) -> str:
    """
    处理折叠块组件 (Collapsible)
    将 [[collapsible show="..." hide="..."]] 语法解析为可编辑的折叠块 HTML 结构。
    取代 FTML 原生渲染，允许在编辑器中可视化地展开/折叠并编辑内容。
    """
    processed_text = text

    def collapsible_replacer(match):
        source = match.group(0)
        params_str = match.group(1).strip()
        content = match.group(2)

        # 解析 show / hide 参数
        show_match = re.search(r'show\s*=\s*"([^"]*)"', params_str)
        hide_match = re.search(r'hide\s*=\s*"([^"]*)"', params_str)
        show_text = show_match.group(1) if show_match else '+ 展开'
        hide_text = hide_match.group(1) if hide_match else '- 收起'

        inner_html = inner_parser_cb(content, theme_type)

        html = (
            f'<div class="scp-component collapsible-box" data-type="collapsible" contenteditable="false">'
            f'<div class="collapsible-header">'
            f'<span class="title-label">显示标题: </span>'
            f'<span class="collapsible-show-title title-input" data-field="show" contenteditable="true">{show_text}</span>'
            f'<span class="title-label" style="margin-left:15px;">隐藏标题: </span>'
            f'<span class="collapsible-hide-title title-input" data-field="hide" contenteditable="true">{hide_text}</span>'
            f'<span class="collapsible-arrow">▶</span>'
            f'</div>'
            f'<div class="collapsible-content-area" contenteditable="true">{inner_html}</div>'
            f'</div>'
        )
        return store.register_html(source, "collapsible", html)

    processed_text = re.sub(
        r'\[\[collapsible([^\]]*)\]\](.*?)\[\[/collapsible\]\]',
        collapsible_replacer,
        processed_text,
        flags=re.DOTALL | re.IGNORECASE
    )

    return processed_text
