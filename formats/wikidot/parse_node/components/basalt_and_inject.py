import re

def parse_theme_basalt(node, state, handle_parse_node_func):
    return ""

def parse_license(node, state, handle_parse_node_func):
    return ""

def parse_toc(node, state, handle_parse_node_func):
    return "\n[[toc]]\n"

def parse_footnote(node, state, handle_parse_node_func):
    content = node.get('data-content', '').strip()
    if state.get('better_footnotes', False):
        return f'[[span class="fnnum"]].[[/span]][[span class="fncon"]]{content}[[/span]]'
    else:
        return f"[[footnote]] {content} [[/footnote]]"

def parse_hr(node, state, handle_parse_node_func):
    return "\n------\n"

def parse_raisa_notice(node, state, handle_parse_node_func):
    style = "border: 1px solid #FFC107; background: #FFFEE0; padding: 15px; margin: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; color: #333; font-family: verdana, arial, helvetica, sans-serif; font-size: 14px; line-height: 1.5;"
    inner = "".join(handle_parse_node_func(c, state) for c in node.select_one('.raisa-content').contents).strip()
    return f"\n[[div style=\"{style}\"]]\n{inner}\n[[/div]]\n"

def parse_class_warning(node, state, handle_parse_node_func):
    style = "background: url(http://scp-wiki.wdfiles.com/local--files/the-great-hippo/scp_trans.png) bottom right no-repeat; border: solid 2px black; padding: 0 20px 20px 20px; margin: 10px auto; width: fit-content; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"
    inner = "".join(handle_parse_node_func(c, state) for c in node.select_one('.class-warning-content > .class-warning-inner').contents)
    inner = re.sub(r'[\n\r]+', '', inner).replace('@@@@', '').replace('@@ @@', '')
    return f"\n[[=]]\n[[div style=\"{style}\"]]\n{inner}\n[[/div]]\n[[/=]]\n"
