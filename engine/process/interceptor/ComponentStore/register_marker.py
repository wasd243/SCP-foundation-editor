import re
import uuid
import html as _html_module

def handle_register_marker(comp, original_source: str, comp_type: str) -> str:
        """注册但不生成外壳，交由 ftml 原生渲染 (如 div, css, 折叠块)"""
        comp_uuid = f"COMP_{uuid.uuid4().hex}"
        safe_source = _html_module.escape(original_source)
        comp.components[comp_uuid] = {
            "uuid": comp_uuid, "source": original_source,
            "safe_source": safe_source, "type": comp_type, "html": "" 
        }
        return comp_uuid