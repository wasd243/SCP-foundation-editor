use super::model::{TocHeadingData, TocPlaceholderData};
use html_escape::encode_text;

pub fn render_placeholder_html() -> String {
    r#"<span class="scp-component" data-type="toc" style="display:none;" contenteditable="false">[[toc]]</span>"#
        .to_string()
}

pub fn render_heading_marker_html(data: &TocHeadingData, marker_uuid: &str) -> String {
    let title = encode_text(&data.title);
    format!(
        "{prefix}{pluses} {marker_uuid}{title}",
        prefix = data.prefix,
        pluses = data.pluses,
        marker_uuid = marker_uuid,
        title = title,
    )
}

pub fn render_marker_html(data: &TocHeadingData) -> String {
    let anchor = encode_text(&data.anchor);
    format!(
        r#"<span class="toc-anchor-marker" data-anchor="{anchor}" style="display:none" contenteditable="false"></span>"#,
        anchor = anchor
    )
}

#[allow(dead_code)]
pub fn _placeholder_debug(_data: &TocPlaceholderData) {}
