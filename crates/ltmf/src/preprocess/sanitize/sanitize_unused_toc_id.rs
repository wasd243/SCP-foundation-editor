use serde_json::Value;

pub fn sanitize_unused_toc_id(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            if is_heading(&map) {
                remove_toc_id(&mut map);
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, sanitize_unused_toc_id(value)))
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(sanitize_unused_toc_id)
                .collect(),
        ),
        _ => value,
    }
}

fn is_heading(map: &serde_json::Map<String, Value>) -> bool {
    map.get("type").and_then(Value::as_str) == Some("heading")
}

fn remove_toc_id(map: &mut serde_json::Map<String, Value>) {
    if let Some(Value::Object(attrs)) = map.get_mut("attrs") {
        attrs.remove("id");
    }
}
