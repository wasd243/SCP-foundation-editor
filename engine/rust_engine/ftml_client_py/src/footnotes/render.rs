use super::model::FootnoteData;

fn escape_html(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}

pub fn render_html(data: &FootnoteData) -> String {
    let escaped = escape_html(&data.content);
    format!(
        r#"<span class="scp-component scp-footnote" data-type="footnote" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-content="{escaped}" title="{escaped}" contenteditable="false">#</span>"#
    )
}
