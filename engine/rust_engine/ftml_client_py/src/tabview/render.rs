use super::model::TabViewData;

pub fn render_html(data: &TabViewData, inner_html: &[String]) -> String {
    let mut header_html = String::new();
    let mut body_html = String::new();

    for (i, tab) in data.tabs.iter().enumerate() {
        let active = if i == 0 { " active" } else { "" };
        let body = inner_html.get(i).cloned().unwrap_or_default();
        header_html.push_str(&format!(
            r#"<span class="tab-btn{active}" contenteditable="true" onclick="selectTab(this)">{title}</span>"#,
            active = active,
            title = tab.title.trim()
        ));
        body_html.push_str(&format!(
            r#"<div class="tab-item{active}" contenteditable="true">{body}</div>"#,
            active = active,
            body = body
        ));
    }

    format!(
        r#"<div class="scp-component tabview-box" data-type="tabview" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false"><div class="tab-header">{header_html}<span class="tab-add" onclick="addTab(this)">+</span></div><div class="tab-contents">{body_html}</div></div>"#,
        header_html = header_html,
        body_html = body_html
    )
}
