import re
import html as _html_module

def process_user(text: str, store) -> str:
    """
    处理用户信息 / 高级用户标示 (User / *User Tag)
    """
    processed_text = text

    def user_replacer(match):
        source = match.group(0)
        name = match.group(1).strip()
        html = f'<span class="scp-component user-tag" data-type="user" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false" style="display:inline-flex; align-items:center; gap:4px; padding:0 2px;"><span class="user-icon" style="background:#aaa; display:inline-block; width:12px; height:12px; border-radius:50%;"></span><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{_html_module.escape(name)}</span></span>&#8203;'
        return store.register_html(source, "user", html)

    processed_text = re.sub(r'\[\[user\s+([^\]]+)\]\]', user_replacer, processed_text, flags=re.IGNORECASE)

    def user_adv_replacer(match):
        source = match.group(0)
        name = match.group(1).strip()
        html = f'<span class="scp-component user-tag" data-type="user-adv" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false" style="display:inline-flex; align-items:center; gap:4px; padding:0 2px;"><span class="user-icon" style="background:gold; display:inline-flex; justify-content:center; align-items:center; width:14px; height:14px; border-radius:50%; color:#fff; font-size:10px;">★</span><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{_html_module.escape(name)}</span></span>&#8203;'
        return store.register_html(source, "user-adv", html)
        
    processed_text = re.sub(r'\[\[\*user\s+([^\]]+)\]\]', user_adv_replacer, processed_text, flags=re.IGNORECASE)

    return processed_text
