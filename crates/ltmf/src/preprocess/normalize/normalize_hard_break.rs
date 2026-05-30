use serde_json::Value;

pub fn normalize_hard_break(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .map(|(key, value)| {
                    if key == "type" && value.as_str() == Some("hardBreak") {
                        (key, Value::String("NewLine".to_string()))
                    } else {
                        (key, normalize_hard_break(value))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.into_iter().map(normalize_hard_break).collect()),
        _ => value,
    }
}
