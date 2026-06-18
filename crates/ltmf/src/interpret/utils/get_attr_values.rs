use serde_json::Value;

/// This function converts a JSON value to a string.
///
/// ---
///
/// It is used at `div.rs` and `span.rs`, when using this function, directly use (if you need a variable)
/// ```ignore
/// let foo = value_to_string(foo)?;
/// ```
pub(crate) fn value_to_string(value: &Value) -> Option<String> {
    match value {
        Value::String(v) => Some(v.clone()),
        Value::Bool(v) => Some(v.to_string()),
        Value::Number(v) => Some(v.to_string()),
        _ => None,
    }
}
