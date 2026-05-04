use super::model::{TocHeadingData, TocPlaceholderData};

fn escape_html(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}

pub fn render_placeholder_html() -> String {
    r#"<span class="scp-component" data-type="toc" style="display:none;" contenteditable="false">[[toc]]</span>"#
        .to_string()
}

pub fn render_heading_marker_html(data: &TocHeadingData, marker_uuid: &str) -> String {
    format!(
        "{prefix}{pluses} {marker_uuid}{title}",
        prefix = data.prefix,
        pluses = data.pluses,
        marker_uuid = marker_uuid,
        title = data.title,
    )
}

pub fn render_marker_html(data: &TocHeadingData) -> String {
    format!(
        r#"<span class="toc-anchor-marker" data-anchor="{anchor}" style="display:none" contenteditable="false"></span>"#,
        anchor = escape_html(&data.anchor)
    )
}

#[allow(dead_code)]
pub fn _placeholder_debug(_data: &TocPlaceholderData) {}
