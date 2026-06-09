use serde_json::Value;

pub(super) fn sanitize_empty_attrs(value: &Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.iter()
                .filter_map(|(key, value)| {
                    let sanitized_value = sanitize_empty_attrs(value);

                    if key == "attrs"
                        && sanitized_value
                            .as_object()
                            .is_some_and(|attrs| attrs.is_empty())
                    {
                        None
                    } else {
                        Some((key.clone(), sanitized_value))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.iter().map(sanitize_empty_attrs).collect()),
        _ => value.clone(),
    }
}
