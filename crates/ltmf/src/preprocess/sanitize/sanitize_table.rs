use serde_json::Value;

pub fn sanitize_table(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if is_default_table_attr(&key, &value) {
                        None
                    } else {
                        Some((key, sanitize_table(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.into_iter().map(sanitize_table).collect()),
        _ => value,
    }
}

fn is_default_table_attr(key: &str, value: &Value) -> bool {
    matches!(key, "colspan" | "rowspan") && value.as_u64() == Some(1)
        || key == "class" && value.as_str() == Some("wiki-content-table")
}
