import os
import json
import re
from formats.wikidot.wikidot_parser import parse_wikidot_to_editor_html

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_JS_INSERT_PATH = os.path.join(CURRENT_DIR, 'js', 'insert_html_at_point.js')


def _load_insert_js():
    try:
        with open(_JS_INSERT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[CSS_INJECTOR] 读取注入模板失败: {e}")
        return None


def _run_inject(page, x, y, html_content):
    """底层执行：json.dumps 序列化，彻底规避转义问题。"""
    js_template = _load_insert_js()
    if js_template is None:
        return
    safe_html_json = json.dumps(html_content)
    final_js = (js_template
                .replace('__POS_X__', str(x))
                .replace('__POS_Y__', str(y))
                .replace('__SAFE_HTML__', safe_html_json))
    page.runJavaScript(final_js)


def _extract_and_parse(wikidot_code, no_hoist_css=False):
    """
    ✅ 核心修复：[[module css]] 块在进入解析器之前先提取出来，
    由我们自己生成 <style> 标签，保留原始缩进和换行格式。
    解析器只负责处理剩余的 wikidot 标记语法。
    """
    css_blocks = []

    def _pull_css(m):
        # strip() 去掉首尾空白，但保留内部所有换行和缩进
        css_blocks.append(m.group(1).strip())
        return ''  # 从 wikidot 代码里删掉这段，让解析器不再接触它

    clean_code = re.sub(
        r'\[\[module\s+css\]\](.*?)\[\[/module\]\]',
        _pull_css,
        wikidot_code,
        flags=re.DOTALL | re.IGNORECASE
    )

    # 只把非 CSS 部分交给 wikidot 解析器
    html_body = parse_wikidot_to_editor_html(clean_code)

    # 手动拼接 <style> 标签，原始格式完整保留
    if css_blocks:
        hoist_attr = ' data-no-hoist="true"' if no_hoist_css else ''
        style_tags = '\n'.join(
            f'<style{hoist_attr}>\n{css}\n</style>'
            for css in css_blocks
        )
        html_body = style_tags + '\n' + html_body

    return html_body


def _inject_wikidot(page, x, y, wikidot_code, no_hoist_css=False):
    html_content = _extract_and_parse(wikidot_code, no_hoist_css)
    _run_inject(page, x, y, html_content)


def _read_template(filename):
    template_path = os.path.join(CURRENT_DIR, 'templates', filename)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[CSS_INJECTOR] 读取模板 {filename} 失败: {e}")
        return ""


# ── 各组件注入函数 ────────────────────────────────────────────────────────────

def inject_terminal_shortcut(page, x, y):
    code_css = _read_template("terminal_shortcut/terminal_shortcut.css")
    code_body = _read_template("terminal_shortcut/terminal_shortcut.txt")
    _inject_wikidot(page, x, y, f"[[module css]]\n{code_css}\n[[/module]]\n{code_body}")


def inject_terminal_001(page, x, y):
    code_css = _read_template("terminal_001/terminal_001.css")
    code_body = _read_template("terminal_001/terminal_001.txt")

    # ✅ 先走 _extract_and_parse，CSS 格式得到保护
    html_content = _extract_and_parse(
        f"[[module css]]\n{code_css}\n[[/module]]\n{code_body}"
    )

    # terminal-001 专属后处理
    def terminal_001_replacer(m):
        inner = m.group(1).replace(
            '<div class="text">',
            '<div class="text" contenteditable="true">'
        )
        return (
            '<div class="terminal scp-component terminal-001-box"'
            ' data-type="div-block" contenteditable="false">'
            f'{inner}</div>'
        )

    html_content = re.sub(
        r'<div class="terminal">(.*?)</div>\s*</div>',
        terminal_001_replacer,
        html_content,
        flags=re.DOTALL
    )
    _run_inject(page, x, y, html_content)


def inject_raisa_notice(page, x, y):
    _inject_wikidot(page, x, y, _read_template("raisa_notice/raisa_notice.txt"))


def inject_class_warning(page, x, y):
    _inject_wikidot(page, x, y, _read_template("class_warning/class_warning.txt"))


def inject_foundation_background(page, x, y):
    code_css = _read_template("foundation_background/foundation_background.css")
    code_body = _read_template("foundation_background/foundation_background.txt")
    code = f"{code_body}\n[[module CSS]]\n{code_css}\n[[/module]]"
    # no_hoist_css=True：这个组件的 CSS 必须跟在元素后面，不能提升到 <head>
    _inject_wikidot(page, x, y, code, no_hoist_css=True)


def inject_o5_command(page, x, y):
    _inject_wikidot(page, x, y, _read_template("o5_command/o5_command.txt"))


def inject_video_record(page, x, y):
    _inject_wikidot(page, x, y, _read_template("video_record/video_record.txt"))


def inject_video_record2(page, x, y):
    _inject_wikidot(page, x, y, _read_template("video_record/video_record2.txt"))


def inject_page_note(page, x, y):
    code_css = _read_template("page_note/page_note.css")
    code_body = _read_template("page_note/page_note.txt")
    _inject_wikidot(page, x, y, f"[[module css]]\n{code_css}\n[[/module]]\n{code_body}")


def inject_email_template(page, x, y):
    code_css = _read_template("email_template/email_template.css")
    code_body = _read_template("email_template/email_template.txt")
    _inject_wikidot(page, x, y, f"[[module css]]\n{code_css}\n[[/module]]\n{code_body}")


def inject_login_logout(page, x, y):
    code_css = _read_template("login_logout/login_logout.css")
    code_body = _read_template("login_logout/login_logout.txt")
    _inject_wikidot(page, x, y, f"[[module css]]\n{code_css}\n[[/module]]\n{code_body}")
