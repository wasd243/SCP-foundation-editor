use crate::import_json::import_json;
use crate::preprocess::adapter::pm_json_reverse_adapter;
use crate::preprocess::normalize::normalize;
use crate::preprocess::sanitize::sanitize;
use serde_json::Value;

mod normalize;
mod sanitize;
mod adapter;

pub fn preprocess(json: &str) -> Result<String, String> {
    let mut json = json.to_string();

    // Test-only JSON, going to be removed after implementation of exporter
    import_json(&mut json);
    // End of test-only JSON

    let json_value: Value = serde_json::from_str(&json).map_err(|error| error.to_string())?;

    // Sanitize the JSON.
    let sanitized_json = sanitize(json_value);

    // Normalize the JSON.
    let normalized_json = normalize(sanitized_json);

    // Adapt editor-specialized PM JSON back to resourcepack include variable names.
    let adapted_json = pm_json_reverse_adapter(normalized_json);

    let json = serde_json::to_string_pretty(&adapted_json).map_err(|error| error.to_string())?;

    Ok(json)
}
