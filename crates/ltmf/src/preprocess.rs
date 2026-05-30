use crate::import_json::import_json;
use crate::preprocess::sanitize::{
    sanitize_contenteditable::sanitize_contenteditable,
    sanitize_data_editor::sanitize_data_editor,
    sanitize_empty_html_attrs::sanitize_empty_html_attrs,
    sanitize_empty_attrs::sanitize_empty_attrs,
    sanitize_null::sanitize_null,
    sanitize_pm_unused_img::sanitize_pm_unused_img,
    sanitize_tabview::sanitize_tabview,
    sanitize_text_align::sanitize_text_align,
    sanitize_wj_inline_tag::sanitize_wj_inline_tag,
};
use serde_json::Value;

pub mod sanitize;
mod normalizer;

pub fn preprocess(json: &str) -> Result<String, String> {
    let mut json = json.to_string();
    import_json(&mut json);

    let json_value: Value = serde_json::from_str(&json).map_err(|error| error.to_string())?;

    let sanitized_json = sanitize_null(&json_value);
    let sanitized_json = sanitize_data_editor(sanitized_json);
    let sanitized_json = sanitize_wj_inline_tag(sanitized_json);
    let sanitized_json = sanitize_text_align(sanitized_json);
    let sanitized_json = sanitize_contenteditable(sanitized_json);
    let sanitized_json = sanitize_tabview(sanitized_json);
    let sanitized_json = sanitize_pm_unused_img(sanitized_json);
    let sanitized_json = sanitize_empty_html_attrs(&sanitized_json);

    // Sanitize empty attrs in the end to ensure that all empty attrs are removed.
    let sanitized_json = sanitize_empty_attrs(&sanitized_json);

    let json = serde_json::to_string_pretty(&sanitized_json).map_err(|error| error.to_string())?;

    Ok(json)
}
