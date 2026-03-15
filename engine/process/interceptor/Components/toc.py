import re

def process_toc(text: str, store, inner_parser_cb, theme_type: str) -> str:
    """
    处理 TOC 相关的拦截：
    1. [[toc]] -> 增强版可视占位符 (展示检测到的标题)
    2. + [[# anchor]] Title -> 还原为原生标题渲染，但注入一个隐藏的锚点 marker
    """
    
    # 1. 预先扫描所有带锚点的标题，用于 TOC 展示
    # 正则匹配: + [[# anchor]] Title
    heading_pattern = r'(?:^|\n)(\+{1,6})\s*\[\[#\s*([^\]]+)\]\]\s*(.*)'
    all_headings = re.findall(heading_pattern, text)
    
    # 2. 处理 [[toc]] 占位符
    def toc_replacer(match):
        source = match.group(0)
        
        # 构建预览列表 (最多展示 6 个)
        preview_list = []
        for h in all_headings[:6]:
            level = len(h[0])
            title = h[2].strip()
            indent = "&nbsp;" * (level - 1) * 4
            preview_list.append(f'<li style="list-style:none; margin: 2px 0;">{indent}<span style="color:#888;">{"·" * level}</span> {title}</li>')
        
        if len(all_headings) > 6:
            preview_list.append('<li style="list-style:none; color:#AAA;">...更多标题...</li>')
            
        list_html = "".join(preview_list) if preview_list else '<li style="list-style:none; color:#999;">（暂无配置锚点的标题条目）</li>'

        html = (
            f'<div class="scp-component toc-placeholder" data-type="toc" contenteditable="false" '
            f'style="border: 1px solid #ccc; background: #f9f9f9; padding: 12px; margin: 15px 0; border-radius: 4px; font-family: sans-serif;">'
            f'<div style="font-weight: bold; color: #333; margin-bottom: 8px; font-size: 1.1em; border-bottom: 1px solid #eee;">'
            f'<span style="color: #c00; margin-right: 5px;">[[</span> 文本目录 (TOC) <span style="color: #c00; margin-left: 5px;">]]</span>'
            f'</div>'
            f'<ul style="margin: 0; padding: 0 5px; font-size: 0.9em; line-height: 1.4; color: #555;">'
            f'{list_html}'
            f'</ul>'
            f'<div style="margin-top: 8px; font-size: 0.8em; color: #999; font-style: italic;">提示: 导出时将自动生成 Wikidot 目录</div>'
            f'</div>'
        )
        return store.register_html(source, "toc", html)

    processed_text = re.sub(r'\[\[toc\]\]', toc_replacer, text, flags=re.IGNORECASE)

    # 3. 处理带锚点的标题
    # 我们不再把整个标题作为组件，而是把锚点变成一个隐藏的 span 标记
    # 这样标题本身保持原生，由 FTML 渲染，从而支持 Enter 换行和格式切换
    def heading_marker_replacer(match):
        prefix = match.group(1)
        pluses = match.group(2)
        anchor = match.group(3).strip()
        title_text = match.group(4).strip()
        
        # 注册一个包含锚点信息的隐藏标记
        marker_html = f'<span class="toc-anchor-marker" data-anchor="{anchor}" style="display:none" contenteditable="false"></span>'
        # 我们使用 register_html 仅仅是为了生成一个 UUID 占位符
        # 这个占位符将被 FTML 包含在其生成的 <hX> 标签内
        marker_uuid = store.register_html(f"[[# {anchor}]]", "toc-anchor-marker", marker_html)
        
        # 返回原生 Wikidot 标题语法，但嵌入了 UUID，并保留前缀（如换行符）
        return f"{prefix}{pluses} {marker_uuid}{title_text}"

    # 修改正则：将 (?:^|\n) 改为 (^|\n) 以便捕获前缀
    heading_pattern = r'(^|\n)(\+{1,6})\s*\[\[#\s*([^\]]+)\]\]\s*(.*)'
    processed_text = re.sub(heading_pattern, heading_marker_replacer, processed_text)

    return processed_text
