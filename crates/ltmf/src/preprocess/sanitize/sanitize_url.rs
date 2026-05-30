use serde_json::Value;

pub fn sanitize_url(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if is_unused_url_attr(&key, &value) {
                        None
                    } else {
                        Some((key, sanitize_url(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.into_iter().map(sanitize_url).collect()),
        _ => value,
    }
}

fn is_unused_url_attr(key: &str, value: &Value) -> bool {
    key == "rel" && value.as_str() == Some("noopener noreferrer nofollow")
        || key == "target" && value.as_str() == Some("_blank")
}
