import uuid
import html as _html_module

def handle_register_html(comp, original_source: str, comp_type: str, html_shell_template: str) -> str:
    """注册并生成自定义交互 UI 外壳"""
    comp_uuid = f"COMP_{uuid.uuid4().hex}"
    safe_source = _html_module.escape(original_source)
    final_html = (html_shell_template
                    .replace("{{uuid}}", comp_uuid)
                    .replace("{{source}}", safe_source))
    comp.components[comp_uuid] = {
        "uuid": comp_uuid, "source": original_source,
        "safe_source": safe_source, "type": comp_type, "html": final_html
    }
    return f"WDKEY{comp_uuid}ENDWDKEY"