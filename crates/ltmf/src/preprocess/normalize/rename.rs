use serde_json::Value;

pub fn rename_type(value: Value, from: &str, to: &str) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .map(|(key, value)| {
                    if key == "type" && value.as_str() == Some(from) {
                        (key, Value::String(to.to_string()))
                    } else {
                        (key, rename_type(value, from, to))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(|value| rename_type(value, from, to))
                .collect(),
        ),
        _ => value,
    }
}
