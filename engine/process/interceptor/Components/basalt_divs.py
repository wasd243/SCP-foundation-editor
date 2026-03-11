import re

basalt_special_map = {
    "blockquote": "basalt-blockquote-box",
    "notation": "basalt-notation-box",
    "jotting": "basalt-jotting-box",
    "modal": "basalt-modal-box",
    "smallmodal": "basalt-smallmodal-box",
    "papernote": "basalt-papernote-box",
    "document": "basalt-document-box",
    "darkdocument": "basalt-darkdocument-box",
    "raisa_memo": "basalt-raisa_memo-box",
    "classification_memo": "basalt-classification_memo-box",
    "ettra_memo": "basalt-ettra_memo-box",
    "ethics_memo": "basalt-ethics_memo-box",
    "temporal_memo": "basalt-temporal_memo-box",
    "overwatch_memo": "basalt-overwatch_memo-box",
    "miscomm_memo": "basalt-miscomm_memo-box"
}

def extract_top_div(txt, start_pos):
    tag_end = txt.find(']]', start_pos)
    if tag_end == -1: return None
    params_str = txt[start_pos + 5 : tag_end].strip()
    depth = 1
    i = tag_end + 2
    while i < len(txt) and depth > 0:
        next_open = txt.find('[[div', i)
        next_close = txt.find('[[/div]]', i)
        if next_close == -1: break
        if next_open != -1 and next_open < next_close:
            depth += 1; i = next_open + 5
        else:
            depth -= 1
            if depth == 0:
                inner = txt[tag_end + 2 : next_close]
                return (params_str, inner, next_close + 8)
            i = next_close + 8
    return None

def process_basalt_divs(text: str, store, inner_parser_cb, theme_type: str) -> str:
    """仅拦截玄武岩专用 DIV 进行交互式 UI 解析，其他 DIV 放行原生渲染"""
    output = []
    cursor = 0
    while True:
        start_idx = text.find('[[div', cursor)
        if start_idx == -1:
            output.append(text[cursor:])
            break
        
        info = extract_top_div(text, start_idx)
        if not info:
            # 格式不完整，不处理
            output.append(text[cursor:start_idx+5])
            cursor = start_idx + 5
            continue
            
        params, inner_content, end_pos = info
        source_div = text[start_idx:end_pos]
        
        class_match = re.search(r'class=["\']([^"\']+)["\']', params)
        classes = class_match.group(1).split() if class_match else []
        
        is_basalt_div = False
        html_shell = ""
        
        # 1. 浮动框
        if "floatbox" in classes:
            is_basalt_div = True
            right_cls = " right" if "right" in classes else ""
            parsed_inner = inner_parser_cb(inner_content, theme_type)
            html_shell = (f'<div class="scp-component div-box basalt-div basalt-floatbox-box{right_cls}" data-type="div-block" contenteditable="false">'
                          f'<div class="div-header" contenteditable="false" onclick="toggleDiv(this)" title="点击折叠/展开">[[div class="{" ".join(classes)}"]]</div>'
                          f'<div class="div-content" contenteditable="true">{parsed_inner}</div></div>')
                          
        # 2. 其他特殊的玄武岩框
        elif any(cls in basalt_special_map for cls in classes):
            is_basalt_div = True
            # Find the primary matching class
            primary_cls = next(cls for cls in classes if cls in basalt_special_map)
            box_cls = basalt_special_map[primary_cls]
            box_classes = ["scp-component", "div-box", "basalt-div", box_cls]
            
            if primary_cls in ["document", "darkdocument"]:
                box_classes.append("basalt-doc-wrapper full-width")
            if primary_cls.endswith("_memo"):
                box_classes.append("basalt-memo-box")
                
            box_cls_str = " ".join(box_classes)
            parsed_inner = inner_parser_cb(inner_content, theme_type)
            html_shell = (f'<div class="{box_cls_str}" data-type="div-block" contenteditable="false">'
                          f'<div class="div-header" contenteditable="false" onclick="toggleDiv(this)" title="点击折叠/展开">[[div class="{" ".join(classes)}"]]</div>'
                          f'<div class="div-content" contenteditable="true">{parsed_inner}</div></div>')
        
        if is_basalt_div:
            output.append(text[cursor:start_idx])
            output.append(store.register_html(source_div, "div-block", html_shell))
            cursor = end_pos
        else:
            # 并不是玄武岩代码，向后推进但要保证不破坏内部嵌套结构，需要继续扫描？
            # 既然整体是一个 DIV 但不需要拦截外壳，那就保留它的 `[[div ...]]` 标签
            # 让游标只跳过开头的 [[div，这样可以继续递归查找它的内部有没有玄武岩div！
            output.append(text[cursor:start_idx+5])
            cursor = start_idx + 5

    return "".join(output)
