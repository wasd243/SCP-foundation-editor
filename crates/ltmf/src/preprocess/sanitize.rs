use serde_json::Value;
use {
    sanitize_contenteditable::sanitize_contenteditable, sanitize_data_editor::sanitize_data_editor,
    sanitize_draggable::sanitize_draggable, sanitize_empty_attrs::sanitize_empty_attrs,
    sanitize_empty_html_attrs::sanitize_empty_html_attrs,
    sanitize_footnote::sanitize_footnote_refs, sanitize_null::sanitize_null,
    sanitize_pm_unused_img::sanitize_pm_unused_img, sanitize_table::sanitize_table,
    sanitize_tabview::sanitize_tabview, sanitize_text_align::sanitize_text_align,
    sanitize_unused_img_attrs::sanitize_unused_img_attrs,
    sanitize_unused_toc_id::sanitize_unused_toc_id, sanitize_url::sanitize_url,
    sanitize_wj_inline_tag::sanitize_wj_inline_tag,
};

mod sanitize_contenteditable;
mod sanitize_data_editor;
mod sanitize_draggable;
mod sanitize_empty_attrs;
mod sanitize_empty_html_attrs;
mod sanitize_footnote;
mod sanitize_null;
mod sanitize_pm_unused_img;
mod sanitize_table;
mod sanitize_tabview;
mod sanitize_text_align;
mod sanitize_unused_img_attrs;
mod sanitize_unused_toc_id;
mod sanitize_url;
mod sanitize_wj_inline_tag;

pub fn sanitize(value: Value) -> Value {
    let value = sanitize_null(&value);
    let value = sanitize_data_editor(value);
    let value = sanitize_wj_inline_tag(value);
    let value = sanitize_text_align(value);
    let value = sanitize_contenteditable(value);
    let value = sanitize_tabview(value);
    let value = sanitize_pm_unused_img(value);
    let value = sanitize_unused_img_attrs(value);
    let value = sanitize_footnote_refs(value);
    let value = sanitize_draggable(value);
    let value = sanitize_table(value);
    let value = sanitize_url(value);
    let value = sanitize_unused_toc_id(value);
    let value = sanitize_empty_html_attrs(&value);

    // Sanitize empty attrs in the end to ensure that all empty attrs are removed.
    sanitize_empty_attrs(&value)
}
