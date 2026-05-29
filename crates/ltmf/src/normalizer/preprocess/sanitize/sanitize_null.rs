use serde_json::Value;

pub fn sanitize_null(value: &Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.iter()
                .filter(|(_, value)| !value.is_null())
                .map(|(key, value)| (key.clone(), sanitize_null(value)))
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.iter().map(sanitize_null).collect()),
        _ => value.clone(),
    }
}
