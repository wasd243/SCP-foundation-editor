use super::model::FakeProtData;

pub fn render_html(data: &FakeProtData, parsed_coll: &str) -> String {
    format!(
        concat!(
            r#"<div class="scp-component login-logout-box" data-type="login-logout" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false" style="border:1px solid #ccc; padding:8px; margin:8px 0; position:relative; clear:both;">"#,
            r#"<table class="login-form-table" contenteditable="false" style="margin:0.5em auto; border-collapse:collapse;"><tr>"#,
            r#"<td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">ID</td>"#,
            r#"<td><span class="login-id-value" contenteditable="true" data-field="id" style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif;">{id_val}</span></td></tr>"#,
            r#"<tr><td style="width:80px; padding:4px 8px; font-family:sans-serif;" contenteditable="false">密码</td>"#,
            r#"<td><span contenteditable="false" style="display:inline-block; border:1px solid #aaa; padding:2px 6px; min-width:200px; font-family:sans-serif; color:#555; letter-spacing:2px;">・・・・・・・・・</span></td></tr>"#,
            r#"<tr><td contenteditable="false"></td><td style="text-align:center;" contenteditable="false"><button contenteditable="false" style="padding:2px 18px; border:1px solid #aaa; background:#f4f4f4;  font-family:sans-serif;">登入</button></td></tr></table>"#,
            r#"<hr contenteditable="false" style="border:none; border-top:1px solid #ccc; margin:6px 0;">"#,
            r#"<div contenteditable="false" style="font-size:11px; color:#888; text-align:center; margin-bottom:4px; font-family:sans-serif;">[登入]↔[登出] 折叠内容</div>"#,
            r#"<div class="login-collapsible-content" contenteditable="true" style="min-height:40px; padding:6px; border:1px dashed #bbb; background:#fafafa;">{parsed_coll}</div></div>"#
        ),
        id_val = data.login_id,
        parsed_coll = parsed_coll
    )
}
