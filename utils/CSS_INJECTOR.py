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

def inject_terminal_shortcut(page, x, y): 
    code = """[[module css]]
.danke{
padding: 5px 5px 5px 15px;
margin-bottom:10px;
font-family: 'Courier New', monospace;
font-size: 1.1em; }

.agent{
background-color:#000000;
border: 3px solid #55AA55;
color: #77CC77;
}

.site{
background-color:#222200;
border: 3px solid #AAAA55;
color: #DDDD77;
}
[[/module]]
[[div class="danke agent"]]
| 细节
| 细节
| 细节
| 细节
| 细节

文字 文字 文字
更多文字

更多

以及更多

甚至还有更多要记录的文字
[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_terminal_001(page, x, y): 
    code = """[[module css]]
div.terminal{
    border: 1px solid black;
    border: solid 3px #BBBBBB;
    border-radius: 16px;
    background-color: #000000;
/* 终端上方的黑色阴影 */
    background-image:
        radial-gradient(ellipse 1000% 100% at 50% 90%, transparent, #121);
    background-position: center;
    display: block;
/* 终端周围的阴影 */
    box-shadow: inset 0 0 10em 1em rgba(0,0,0,0.5);
/* 防止扫描条产生滚动条 */
    overflow:hidden;
}
div.terminal blockquote {
    background-color: black;
    border: double 3px #80FF80;
    color: #80FF80;
}
div.scanline{
    margin-top: -40%;
    width: 100%;
    height: 60px;
    position: relative;
    pointer-events: none;
/* Safari 4.0 - 8.0 */
    -webkit-animation: scan 12s linear 0s infinite; /* 你可能需要修改这个。如果扫描条走得太快了，添加5秒。 */
    animation: scan 12s linear 0s infinite; /* 同上 */
    background: linear-gradient(to bottom, rgba(56, 112, 82,0), rgba(56, 112, 82,0.1)) !important;
}

div.text{
    color: rgba(128,255,128,0.8);
    padding-left: 2em;
    padding-top: 40%;
    font-family: 'Courier New', monospace;
    font-size: 1.2em;
    }

/* Safari 4.0 - 8.0 */
@-webkit-keyframes scan{
    from{ transform: translateY(-10%);}
    to{  transform: translateY(5000%);} /* 你可能需要根据你终端的长短修改这个。如果扫描条走到一半停止了，增大第二个数字。 */
}

@keyframes scan{
    from{ transform: translateY(-10%);}
    to{  transform: translateY(5000%);} /* 同上。 */
}

div.text a {
    color: #90EE90;
    text-decoration: none;
    background: transparent;
}
div.text a.newpage {
    color: #90EE90;
    text-decoration: none;
    background: transparent;
}
div.text a:hover {
    color: #131;
    text-decoration: underline;
    background-color: #80FF80;
    padding: 1px;
}
div.text a:hover::before{
content: "> ";
}
[[/module]]
[[div class="terminal"]]
[[div class="scanline"]][[/div]]
[[div class="text"]]
[[=]]
[[size 150%]]__终端 #001__[[/size]]
@@ @@
@@ @@
@@------@@
欢迎，用户
@@------@@
[[/=]]
@@ @@
@@ @@
@@ @@
> 终端内部的链接会在鼠标移过时显示“>”。
> [http://www.baidu.com 就像这样]

谢谢你查看我的格式！
@@ @@
@@ @@
[[/div]]
[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_raisa_notice(page, x, y): 
    code = """[[div style="border:solid 1px #999999; background:#f2f2c2; padding:5px; margin-bottom: 10px;"]]
[[=]]
[[size larger]] **基金会记录与信息安全管理部的通知** [[/size]]

通知在此

-- Maria Jones，RAISA主管
[[/=]]
[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_class_warning(page, x, y): 
    code = """[[=]]
[[div style="background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) center no-repeat; float: center; border: solid 2px #000; padding: 1px 15px; box-shadow: 0 1px 3px rgba(0,0,0,.2);"]]
##ff5c48|[[size 150%]] **警告：下列文件为#/XXXX级机密** [[/size]]##
----
[[size larger]] **无#/XXXX级权限下访问将被记录并立即处以纪律处分。** [[/size]]
[[/div]]
[[/=]]"""
    _inject_wikidot(page, x, y, code)

def inject_foundation_background(page, x, y): 
    code = """[[div class="orderwrapper"]]
[[div class="council1"]]
[[/div]]
[[div class="ordertitle"]]
+* 标题
[[/div]]
[[div class="orderdescription"]]
 _
+* 副标题
描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述 描述
[[/div]]
[[div class="itemno"]]
+* XXXX
[[/div]]
[[/div]]

[[module CSS]]
.orderwrapper {position: relative;width: auto;text-align: center;}.council1 {position: relative;top: 0;bottom: 0;left: 0;right: 0;width: 295px;height: 295px;margin: auto;background-image: url( "http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png" );background-size: 295px 295px;background-repeat: no-repeat;background-position: center;}.ordertitle {position: absolute;left: 0;right: 0;top: 38px;}.ordertitle h1 {font-size: 220%;color: #555;}.orderdescription {position: absolute;left: 0;right: 0;top: 85px;width: 100%;}.orderdescription p {font-size: 90%;color: #555;}.orderdescription h1 {font-size: 120%;color: #555;}.itemno {position: absolute;left: 0;right: 0;bottom: 27px;}.itemno h1 {font-size: 170%;color: #555;}
[[/module]]"""
    _inject_wikidot(page, x, y, code)

def inject_o5_command(page, x, y): 
    code = """[[div style="background: url(http://kaktuskontainer.wdfiles.com/local--files/format-hell/scp_trans.png) bottom center no-repeat; text-align: center; width: 600px; margin: 0 auto; font-size: 20px; padding: 0px;"]]
@@ @@
@@ @@
@@ @@
@@ @@
[[=]]
++* ##black|根据监督者议会的命令##
##black|以下文件为X/XXXX级机密。禁止未经授权的访问。##
[[/=]]
= **##black|XXXX##**
@@ @@
@@ @@
[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_video_record(page, x, y): 
    code = """[[div class="blockquote"]]
= **视频记录**
----
**日期：**

**笔记：**
----

[记录开始]

**时间：**事件

**时间：**事件

**时间：**事件

-----

[记录结束]
[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_video_record2(page, x, y): 
    code = """[[div class="blockquote" style="border-radius: 10px; margin: 10px"]]
**视频日志记录**

**日期：**可选

**探索队伍：**队伍名称 - 可选

**目标：**区域/异常 - 可选

**领队：**可选

**小队成员：**可选

-----

[记录开始]

**人物A：**对白

**人物B：**对白

//事件发生//

**人物A：**对白

[记录结束]

[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_page_note(page, x, y): 
    code = """[[module css]]
.page {
    display: block;
    overflow: hidden;
    font-family: "Monotype Corsiva", "Bradley Hand ITC", sans-serif;
    font-style: normal;

    background-attachment: scroll;
    background-clip: border-box;
    background-color: transparent;
    background-image: linear-gradient(to top ,rgb(202, 219, 228) 0%, rgb(231, 233, 220) 8%);
    background-origin: padding-box;
    background-position: 0px 8px;
    background-repeat: repeat;
    background-size: 100% 20px;

    border: 1px solid #CCC;
    border-radius: 10px;
    padding: 10px 10px;
    margin-bottom: 10px;

    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.2)
    }
.page p,
.page ul {
    line-height: 20px;
    margin: 0;
}
[[/module]]
[[div class="page"]]
正文在此。你需要在新的一行中使用“@<@@ @@>@”来正确地分行。
@@ @@
就像这样。
@@ @@
你可以使用[[<]]，[[=]]，[[>]]来将不同文本/段落以你的方式对齐。
@@ @@
[[>]]
尽情享受
[[/>]]
[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_email_template(page, x, y): 
    code = """[[module CSS]]
.email-example .collapsible-block-folded a.collapsible-block-link {
    animation: blink 0.8s ease-in-out infinite alternate;
}
@keyframes blink {
    0% { color: transparent; }
    50%, 100% { color: #b01; }
}
.email {border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.5)}
.email-example a.collapsible-block-link {font-weight: bold;}
.tofrom {margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon}
[[/module]]
[[div class="email-example"]]
[[=]]
------
[[collapsible show="访问SCiPNET邮件？一 (1) 封新邮件！" hide="回复：主题"]]
[[<]]
[[div class="email"]]
[[div class="tofrom"]]
**至：**收件人
**自：**发件人
**主题：**主题
[[/div]]
------
文本
[[/div]]
@@ @@
[[div class="email"]]
[[div class="tofrom"]]
**至：**收件人
**自：**发件人
**主题：**回复：主题
[[/div]]
------
文本
[[/div]]
[[/<]]
[[/collapsible]]
[[/=]]
[[/div]]"""
    _inject_wikidot(page, x, y, code)

def inject_login_logout(page, x, y): 
    code = """[[module CSS]]
.fakeprot .mailform-box .buttons{display:none;}
.fakeprot + .collapsible-block .collapsible-block-link {padding: 0.1em 0.5em;text-decoration: none;background-color: #F4F4F4;border: 1px solid #AAA;color: #000;}
.fakeprot + .collapsible-block .collapsible-block-link:hover {background-color: #DDD;color: #000;}
.fakeprot + .collapsible-block .collapsible-block-link:active {background-color: #DDD;color: #000;}
.fakeprot + .collapsible-block .collapsible-block-unfolded-link{margin:0.5em 0;text-align: center;}
.fakeprot + .collapsible-block .collapsible-block-folded{margin:0.5em 0;text-align: center;}
.fakeprot .passw input[type=text] {text-security:disc;-webkit-text-security:disc;-mox-text-security:disc;}
.mailform-box td:first-child {width: 80px;}
[[/module]]
[[div class="fakeprot"]]
[[module MailForm to="aaaa (DUMMY)" button=""]]
# name
 * title: ID
 * default: <你的ID>
 * type: text
 * rules:
  * required: true
  * maxLength:10
  * minLength: 100
[[/module]]
[[div class="passw"]]
[[module MailForm to="aaaa (DUMMY)" button=""]]
# affiliation
 * title: 密码
 * default: ・・・・・・・・・
 * rules:
  * required: true
  * maxLength:10
  * minLength: 100
[[/module]]
[[/div]]
[[/div]]
[[collapsible show="登入" hide="登出"]]
文字
[[/collapsible]]
"""
    _inject_wikidot(page, x, y, code)