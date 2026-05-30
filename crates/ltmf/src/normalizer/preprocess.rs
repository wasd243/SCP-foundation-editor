use serde_json::Value;
use crate::import_json::import_json;

use crate::normalizer::preprocess::sanitize::{
    sanitize_empty_attrs::sanitize_empty_attrs,
    sanitize_null::sanitize_null,
    sanitize_data_editor::sanitize_data_editor,
};

pub mod sanitize;

pub fn preprocess(json: &str) -> Result<String, String> {
    let mut json = json.to_string();
    import_json(&mut json);

    let json_value: Value = serde_json::from_str(&json).map_err(|error| error.to_string())?;

    let sanitized_json = sanitize_null(&json_value);
    let sanitized_json = sanitize_data_editor(sanitized_json);
    let sanitized_json = sanitize_empty_attrs(&sanitized_json);

    let json = serde_json::to_string_pretty(&sanitized_json).map_err(|error| error.to_string())?;

    Ok(json)
}
