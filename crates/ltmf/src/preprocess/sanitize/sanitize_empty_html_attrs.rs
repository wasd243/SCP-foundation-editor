use serde_json::Value;

pub fn sanitize_empty_html_attrs(value: &Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.iter()
                .filter_map(|(key, value)| {
                    if key == "htmlAttributes"
                        && value.as_object().is_some_and(|attrs| attrs.is_empty())
                    {
                        None
                    } else {
                        Some((key.clone(), sanitize_empty_html_attrs(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => {
            Value::Array(values.iter().map(sanitize_empty_html_attrs).collect())
        }
        _ => value.clone(),
    }
}
