// Normalize include only normalizes the wjBlockTag to include
// This function recursively normalizes matching wjBlockTag nodes to Include.
use serde_json::Value;

pub fn normalize_include(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            let is_include = is_include_node(&Value::Object(map.clone()));

            if is_include {
                map.insert("type".to_string(), Value::String("Include".to_string()));
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, normalize_include(value)))
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(values.into_iter().map(normalize_include).collect()),
        _ => value,
    }
}

fn is_include_node(value: &Value) -> bool {
    value.get("type").and_then(Value::as_str) == Some("wjBlockTag")
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attrs| html_attrs.get("data-editor-export"))
            .and_then(Value::as_str)
            == Some("include")
}
