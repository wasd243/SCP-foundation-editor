import os
import json
from formats.wikidot.wikidot_parser import parse_wikidot_to_editor_html

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def _inject_wikidot(page, x, y, wikidot_code):
    """
    通用注入引擎: 将原始 Wikidot 语法编译为最终 HTML 并传递给前端注入模板
    """
    html_content = parse_wikidot_to_editor_html(wikidot_code)
    # 安全转义 HTML 供 JS 模板字面量使用
    safe_html = html_content.replace('\\', '\\\\').replace('`', '\\`')
    
    js_path = os.path.join(CURRENT_DIR, 'js', 'insert_html_at_point.js')
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()
        
        final_js = js_template.replace('__POS_X__', str(x)).replace('__POS_Y__', str(y)).replace('__SAFE_HTML__', f"`{safe_html}`")
        page.runJavaScript(final_js)
    except Exception as e:
        print(f"执行 HTML 注入脚本失败: {e}")

# =========================================================================
# 以下各组件已被重构为直接传递原始 Wikidot 代码
# =========================================================================

def _read_template(filename):
    """读取模板文件内容"""
    template_path = os.path.join(CURRENT_DIR, 'templates', filename)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取模板 {filename} 失败: {e}")
        return ""

# 终端样式
def inject_terminal_shortcut(page, x, y): 
    code_css = _read_template("terminal_shortcut/terminal_shortcut.css")
    code_body = _read_template("terminal_shortcut/terminal_shortcut.txt")
    code = f"""[[module css]]
{code_css}
[[/module]]
{code_body}"""
    _inject_wikidot(page, x, y, code)

# 终端#001
def inject_terminal_001(page, x, y): 
    code_css = _read_template("terminal_001/terminal_001.css")
    code_body = _read_template("terminal_001/terminal_001.txt")
    code = f"""[[module css]]
{code_css}
[[/module]]
{code_body}"""
    _inject_wikidot(page, x, y, code)

# RAISA通知
def inject_raisa_notice(page, x, y): 
    code_body = _read_template("raisa_notice/raisa_notice.txt")
    code = f"""{code_body}"""
    _inject_wikidot(page, x, y, code)

# 等级警告
def inject_class_warning(page, x, y): 
    code_body = _read_template("class_warning/class_warning.txt")
    code = f"""{code_body}"""
    _inject_wikidot(page, x, y, code)

# 基金会背景
def inject_foundation_background(page, x, y): 
    code_css = _read_template("foundation_background/foundation_background.css")
    code_body = _read_template("foundation_background/foundation_background.txt")
    code = f"""{code_body}
    [[module CSS]]
    {code_css}
    [[/module]]"""
    _inject_wikidot(page, x, y, code)

# O5指令
def inject_o5_command(page, x, y): 
    code_body = _read_template("o5_command/o5_command.txt")
    code = f"""{code_body}"""
    _inject_wikidot(page, x, y, code)

# 视频记录
def inject_video_record(page, x, y): 
    code_body = _read_template("video_record/video_record.txt")
    code = f"""{code_body}"""
    _inject_wikidot(page, x, y, code)

# 视频记录2
def inject_video_record2(page, x, y): 
    code_body = _read_template("video_record/video_record2.txt")
    code = f"""{code_body}"""
    _inject_wikidot(page, x, y, code)

# 笔记
def inject_page_note(page, x, y): 
    code_css = _read_template("page_note/page_note.css")
    code_body = _read_template("page_note/page_note.txt")
    code = f"""[[module css]]
{code_css}
[[/module]]
{code_body}"""
    _inject_wikidot(page, x, y, code)

# 邮件模板
def inject_email_template(page, x, y): 
    code_css = _read_template("email_template/email_template.css")
    code_body = _read_template("email_template/email_template.txt")
    code = f"""[[module css]]
{code_css}
[[/module]]
{code_body}"""
    _inject_wikidot(page, x, y, code)

# 登录登出
def inject_login_logout(page, x, y): 
    code_css = _read_template("login_logout/login_logout.css")
    code_body = _read_template("login_logout/login_logout.txt")
    code = f"""[[module css]]
{code_css}
[[/module]]
{code_body}"""
    _inject_wikidot(page, x, y, code)