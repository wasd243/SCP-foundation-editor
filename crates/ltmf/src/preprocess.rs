use crate::import_json::import_json;
use crate::preprocess::normalize::normalize_hard_break::normalize_hard_break;
use crate::preprocess::sanitize::sanitize;
use serde_json::Value;

mod sanitize;
mod normalize;

pub fn preprocess(json: &str) -> Result<String, String> {
    let mut json = json.to_string();

    // Test-only JSON, going to be removed after implementation of exporter
    import_json(&mut json);
    // End of test-only JSON

    let json_value: Value = serde_json::from_str(&json).map_err(|error| error.to_string())?;

    // Sanitize the JSON.
    let sanitized_json = sanitize(json_value);

    // Normalize hard break to NewLine.
    let normalized_json = normalize_hard_break(sanitized_json);

    let json = serde_json::to_string_pretty(&normalized_json)
        .map_err(|error| error.to_string())?;

    Ok(json)
}
