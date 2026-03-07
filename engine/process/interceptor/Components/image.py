import re

def process_image(text: str, store) -> str:
    """
    处理图片块组件 (Image Block)
    解析原生 [[include component:image-block]]，将其包裹为一个复杂的、带控制柄的 <div> 结构
    并将原始代码作为 data-source 存起来方便导出时原样复原
    """
    processed_text = text

    # 将居中的语法转化为对齐属性
    def wrap_center(m):
        content = m.group(1)
        if re.search(r'align=[^|\]\n]+', content, re.IGNORECASE): 
            content = re.sub(r'align=[^|\]\n]+', 'align=center', content, flags=re.IGNORECASE)
        else: 
            content = content.replace(']]', ' |align=center]]')
        return content
        
    processed_text = re.sub(r'\[\[=\]\]\s*(\[\[include component:image-block.*?\]\])\s*\[\[/=\]\]', wrap_center, processed_text, flags=re.DOTALL | re.IGNORECASE)

    def img_replacer(match):
        source = match.group(0)
        def get_arg(name): 
            m = re.search(fr'(?:\||\s+)\s*{name}\s*=\s*([^\|\n\]]+)', source, re.IGNORECASE)
            return m.group(1).strip() if m else ""
            
        name = get_arg('name')
        caption = get_arg('caption')
        width = get_arg('width')
        height = get_arg('height')
        align = get_arg('align') or 'right'
        
        img_style = "max-width:100%; display:block; margin:0 auto 5px auto;"
        if width: img_style += f" width:{width.lower().strip() if width.endswith(('px','%')) else width+'px'};"
        if height: img_style += f" height:{height.lower().strip() if height.endswith(('px','%')) else height+'px'};"
        if align == 'center': img_style += " width:100% !important;"
        
        dim_html = f'''<div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div style="display:flex; align-items:center;"><b style="flex-shrink:0;">源: &nbsp;</b><span data-field="name" style="display:none;">{name}</span><span class="img-link-label" onclick="editImgLink(this)" onmousedown="event.stopPropagation();" style="color:blue; text-decoration:underline; cursor:pointer;">链接</span></div><div style="display:flex; justify-content:space-between; align-items:baseline;"><span><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{width}</span></span> <span><b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{height}</span></span></div></div>'''
        
        html = f'''<div class="scp-component image-block-box" data-type="image-block-adv" data-align="{align}" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'center')" onmousedown="event.stopPropagation();">置中</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div>{dim_html}</div><div class="image-block-content"><img src="{name}" class="img-preview" style="{img_style}"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;display:none;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">{caption}</span></div></div>'''
        
        return store.register_html(source, "image-block", html)

    processed_text = re.sub(r'\[\[include component:image-block.*?\]\]', img_replacer, processed_text, flags=re.DOTALL)
    
    return processed_text
