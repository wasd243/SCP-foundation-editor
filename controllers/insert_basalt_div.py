import os
import json
from PyQt6.QtGui import QCursor

# 获取当前文件所在的目录 (即 controllers 目录)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def handle_insert_basalt_div(ui, class_name):
    """处理玄武岩版式专用 DIV 的插入逻辑"""
    
    # 1. 确定占位文本内容
    content = "正文在此。"
    if class_name == "blockquote": label = "引用/笔记"
    elif class_name == "notation": label = "高级引用/笔记"
    elif class_name == "jotting": label = "虚线框"
    elif class_name == "modal": label = "调试用笔记"
    elif class_name == "smallmodal": label = "小号调试用笔记"
    elif "floatbox" in class_name: label = "浮动框"
    elif class_name == "raisa_memo": content = "来自记录与信息安全管理部的通知"
    elif class_name == "classification_memo": content = "分级委员会备忘录"
    elif class_name == "ettra_memo": content = "来自潜在战术威胁响应局的通知"
    elif class_name == "ethics_memo": content = "伦理委员会备忘录"
    elif class_name == "temporal_memo": content = "时间异常部门"
    elif class_name == "overwatch_memo": content = "监督者指挥部"
    elif class_name == "miscomm_memo": content = "来自误传部门的通知"
        
    # 2. 获取当前光标坐标
    pos = ui.browser.mapFromGlobal(QCursor.pos())
    
    # 3. 动态读取并组装 JS
    js_path = os.path.join(CURRENT_DIR, 'js', 'insert_basalt_div.js')
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()
        
        # 安全转义字符串
        safe_class = json.dumps(class_name)
        safe_content = json.dumps(content)
        
        # 链式替换四个占位符
        final_js = (js_template.replace('__CLASS_NAME__', safe_class)
                              .replace('__CONTENT__', safe_content)
                              .replace('__POS_X__', str(pos.x()))
                              .replace('__POS_Y__', str(pos.y())))
        
        # 4. 执行注入
        ui.browser.page().runJavaScript(final_js)
        
    except Exception as e:
        print(f"读取玄武岩 DIV 模板失败 ({js_path}): {e}")