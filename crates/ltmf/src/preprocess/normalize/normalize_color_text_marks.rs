use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

pub fn normalize_color_text_marks(value: Value) -> Value {
    let value = rename_type(value, "textColor", "ColorText");
    normalize_color_text_attrs(value)
}

fn normalize_color_text_attrs(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            if map.get("type").and_then(Value::as_str) == Some("ColorText") {
                if let Some(color) = map
                    .get("attrs")
                    .and_then(|attrs| attrs.get("color"))
                    .cloned()
                {
                    map.insert("color".to_string(), color);
                }

                map.remove("attrs");
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, normalize_color_text_attrs(value)))
                    .collect(),
            )
        }
        Value::Array(values) => {
            Value::Array(values.into_iter().map(normalize_color_text_attrs).collect())
        }
        _ => value,
    }
}
