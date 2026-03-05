import os

# 获取当前文件所在的目录 (即 utils 目录)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def _run_injection(page, x, y, filename):
    """通用的 JS 模板读取与执行核心"""
    js_path = os.path.join(CURRENT_DIR, 'js', filename)
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            js_template = f.read()
        
        # 只替换坐标占位符，安全又高效
        final_js = js_template.replace('__POS_X__', str(x)).replace('__POS_Y__', str(y))
        page.runJavaScript(final_js)
    except Exception as e:
        print(f"读取组件注入脚本失败 ({js_path}): {e}")

# =========================================================================
# 以下所有的注入动作，全部变成了极其清爽的单行转发！
# 对应 utils/js/ 目录下的各自 js 模板
# =========================================================================
def inject_terminal_shortcut(page, x, y): _run_injection(page, x, y, 'inject_terminal_shortcut.js')
def inject_terminal_001(page, x, y): _run_injection(page, x, y, 'inject_terminal_001.js')
def inject_raisa_notice(page, x, y): _run_injection(page, x, y, 'inject_raisa_notice.js')
def inject_class_warning(page, x, y): _run_injection(page, x, y, 'inject_class_warning.js')
def inject_foundation_background(page, x, y): _run_injection(page, x, y, 'inject_foundation_bg.js')
def inject_o5_command(page, x, y): _run_injection(page, x, y, 'inject_o5_command.js')
def inject_video_record(page, x, y): _run_injection(page, x, y, 'inject_video_record.js')
def inject_video_record2(page, x, y): _run_injection(page, x, y, 'inject_video_record2.js')
def inject_page_note(page, x, y): _run_injection(page, x, y, 'inject_page_note.js')
def inject_email_template(page, x, y): _run_injection(page, x, y, 'inject_email_template.js')
def inject_login_logout(page, x, y): _run_injection(page, x, y, 'inject_login_logout.js')