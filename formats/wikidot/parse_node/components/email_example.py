def parse_email_example(node, state, handle_parse_node_func):
    show_title = node.select_one('.email-show-title').get_text(strip=True) if node.select_one('.email-show-title') else "访问SCiPNET邮件？一 (1) 封新邮件！"
    hide_title = node.select_one('.email-hide-title').get_text(strip=True) if node.select_one('.email-hide-title') else "回复：主题"
    to1 = node.select_one('.email-to1').get_text(strip=True) if node.select_one('.email-to1') else "收件人"
    from1 = node.select_one('.email-from1').get_text(strip=True) if node.select_one('.email-from1') else "发件人"
    subj1 = node.select_one('.email-subj1').get_text(strip=True) if node.select_one('.email-subj1') else "主题"
    c1_node = node.select_one('.email-content1')
    cont1 = "".join(handle_parse_node_func(c, state) for c in c1_node.contents).strip() if c1_node else "文本"

    to2 = node.select_one('.email-to2').get_text(strip=True) if node.select_one('.email-to2') else "收件人"
    from2 = node.select_one('.email-from2').get_text(strip=True) if node.select_one('.email-from2') else "发件人"
    subj2 = node.select_one('.email-subj2').get_text(strip=True) if node.select_one('.email-subj2') else "回复：主题"
    c2_node = node.select_one('.email-content2')
    cont2 = "".join(handle_parse_node_func(c, state) for c in c2_node.contents).strip() if c2_node else "文本"

    return f'\n[[div class="email-example"]]\n[[=]]\n------\n[[collapsible show="{show_title}" hide="{hide_title}"]]\n[[<]]\n[[div class="email"]]\n[[div class="tofrom"]]\n**至：**{to1}\n**自：**{from1}\n**主题：**{subj1}\n[[/div]]\n------\n{cont1}\n[[/div]]\n@@ @@\n[[div class="email"]]\n[[div class="tofrom"]]\n**至：**{to2}\n**自：**{from2}\n**主题：**{subj2}\n[[/div]]\n------\n{cont2}\n[[/div]]\n[[/<]]\n[[/collapsible]]\n[[/=]]\n[[/div]]\n'
