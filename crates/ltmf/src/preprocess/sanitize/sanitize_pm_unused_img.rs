use serde_json::Value;

pub fn sanitize_pm_unused_img(value: Value) -> Value {
    sanitize_value(value).unwrap_or(Value::Null)
}

fn sanitize_value(value: Value) -> Option<Value> {
    match value {
        Value::Object(map) => {
            if is_unused_pm_image(&Value::Object(map.clone())) {
                None
            } else {
                Some(Value::Object(
                    map.into_iter()
                        .filter_map(|(key, value)| sanitize_value(value).map(|value| (key, value)))
                        .collect(),
                ))
            }
        }
        Value::Array(values) => Some(Value::Array(
            values.into_iter().filter_map(sanitize_value).collect(),
        )),
        _ => Some(value),
    }
}

fn is_unused_pm_image(value: &Value) -> bool {
    value.as_object().is_some_and(|map| {
        map.get("type").and_then(Value::as_str) == Some("image")
            && map
                .get("attrs")
                .and_then(|attrs| attrs.get("src"))
                .and_then(Value::as_str)
                .is_none_or(|src| src.is_empty())
    })
}
