use super::model::{UserData, UserKind};

fn escape_html(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}

pub fn render_html(data: &UserData) -> String {
    let (data_type, icon_style, icon_html) = match data.kind {
        UserKind::Basic => (
            "user",
            "background:#aaa; display:inline-block; width:12px; height:12px; border-radius:50%;",
            "",
        ),
        UserKind::Advanced => (
            "user-adv",
            "background:gold; display:inline-flex; justify-content:center; align-items:center; width:14px; height:14px; border-radius:50%; color:#fff; font-size:10px;",
            "★",
        ),
    };

    let name = escape_html(&data.name);
    format!(
        r#"<span class="scp-component user-tag" data-type="{data_type}" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false" style="display:inline-flex; align-items:center; gap:4px; padding:0 2px;"><span class="user-icon" style="{icon_style}">{icon_html}</span><span class="user-name" contenteditable="true" style="color:#b01; font-weight:bold;">{name}</span></span>&#8203;"#,
    )
}
