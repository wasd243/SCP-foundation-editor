import re
import uuid
import html as _html_module
# import ComponentStore
from engine.process.interceptor.Components.register_html import handle_register_html
from engine.process.interceptor.Components.register_marker import handle_register_marker
# import ACSInterceptor
from engine.process.interceptor.Components.ACSInterceptor import process_acs
# import footnotes
from engine.process.interceptor.Components.footnotes import process_footnotes
from engine.process.interceptor.Components.image import process_image
from engine.process.interceptor.Components.License import process_license
from engine.process.interceptor.Components.AIM import process_aim
from engine.process.interceptor.Components.TabView import process_tabview
from engine.process.interceptor.Components.user import process_user
from engine.process.interceptor.Components.fakeprot import process_fakeprot
from engine.process.interceptor.Components.collapsible import process_collapsible
from engine.process.interceptor.Components.basalt_divs import process_basalt_divs

class ComponentStore:
    """组件金库：负责存储并分发所有被拦截的组件"""
    def __init__(self):
        self.components = {}

    def register_html(self, original_source: str, comp_type: str, html_shell_template: str) -> str:
        """注册并生成自定义交互 UI 外壳"""
        # 直接调用外部文件传入的逻辑，注意将 self 作为 comp 参数传入
        return handle_register_html(self, original_source, comp_type, html_shell_template)

    def register_marker(self, original_source: str, comp_type: str) -> str:
        """注册但不生成外壳，交由 ftml 原生渲染 (如 div, css, 折叠块)"""
        return handle_register_marker(self, original_source, comp_type)

    def get_all(self): return self.components
    def clear(self): self.components.clear()


class ComponentInterceptor:
    def __init__(self):
        self.store = ComponentStore()

    def intercept(self, text: str, theme_type: str, inner_parser_cb) -> tuple[str, ComponentStore]:
        self.store.clear()
        processed_text = text
        
        # 1. 基础预清理
        processed_text = re.sub(r'\[\[<\]\]\s*\[\[module Rate\]\]\s*\[\[/<\]\]', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[>\]\]\s*\[\[module Rate\]\]\s*\[\[/>\]\]', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[module Rate\]\]', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[include :scp-wiki-cn:theme:.*?\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[include :scp-wiki:component:.*?\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[include :scp-wiki-cn:component:betterfootnotes.*?\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)
        processed_text = re.sub(r'\[\[footnoteblock\]\]\r?\n?', '', processed_text, flags=re.IGNORECASE)

        # 2. 脚注
        processed_text = process_footnotes(processed_text, self.store)

        # 3. 授权引用
        processed_text = process_license(processed_text, self.store)

        # 4. ACS 异常分级
        processed_text = process_acs(processed_text, self.store)

        # 5. AIM
        processed_text = process_aim(processed_text, self.store)

        # 6. 图片块
        processed_text = process_image(processed_text, self.store)

        # 7. Tabview
        processed_text = process_tabview(processed_text, self.store, inner_parser_cb, theme_type)

        # 8. 用户信息 (User) 
        processed_text = process_user(processed_text, self.store)

        # 8-B. 登入登出 (Fakeprot) 
        processed_text = process_fakeprot(processed_text, self.store, inner_parser_cb, theme_type)

        # 9. 折叠块 (Collapsible) - 拦截解析，生成交互式 UI 外壳
        processed_text = process_collapsible(processed_text, self.store, inner_parser_cb, theme_type)

        # 10. 玄武岩专用代码 拦截与解析（非玄武岩 div 交由 ftml 原生处理）
        if theme_type == 'basalt' or 'theme:basalt' in text.lower():
            processed_text = process_basalt_divs(processed_text, self.store, inner_parser_cb, theme_type)

        # 11. CSS 拦截与注入 - 暂时交给 ftml 原生解析，不注入 UUID
        def css_replacer(match):
            pass
        # 跳过正则表达式替换，保留原样
        # processed_text = re.sub(r'\[\[module CSS\]\](.*?)\[\[/module\]\]', css_replacer, processed_text, flags=re.DOTALL|re.IGNORECASE)

        return processed_text, self.store