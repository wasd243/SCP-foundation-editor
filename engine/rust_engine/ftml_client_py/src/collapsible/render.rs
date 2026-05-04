use super::model::CollapsibleData;

pub fn render_html(data: &CollapsibleData, inner_html: &str) -> String {
    format!(
        r#"<div class="scp-component collapsible-box" data-type="collapsible" contenteditable="false"><div class="collapsible-header"><span class="title-label">显示标题: </span><span class="collapsible-show-title title-input" data-field="show" contenteditable="true">{show_text}</span><span class="title-label" style="margin-left:15px;">隐藏标题: </span><span class="collapsible-hide-title title-input" data-field="hide" contenteditable="true">{hide_text}</span><span class="collapsible-arrow">▶</span></div><div class="collapsible-content-area" contenteditable="true">{inner_html}</div></div>"#,
        show_text = data.show_text,
        hide_text = data.hide_text,
        inner_html = inner_html
    )
}
