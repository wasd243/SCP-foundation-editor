use super::model::FootnoteData;
use html_escape::encode_text;

pub fn render_html(data: &FootnoteData) -> String {
    let escaped = encode_text(&data.content);
    format!(
        r#"<span class="scp-component scp-footnote" data-type="footnote" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-content="{escaped}" title="{escaped}" contenteditable="false">#</span>"#
    )
}
