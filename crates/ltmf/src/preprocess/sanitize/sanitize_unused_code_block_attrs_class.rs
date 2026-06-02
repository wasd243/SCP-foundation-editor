use serde_json::{Map, Value};

pub fn sanitize_unused_code_block_attrs_class(value: Value) -> Value {
    match value {
        Value::Object(map) => sanitize_object(map),
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(sanitize_unused_code_block_attrs_class)
                .collect(),
        ),
        _ => value,
    }
}

fn sanitize_object(map: Map<String, Value>) -> Value {
    let is_code_block = map.get("type").and_then(Value::as_str) == Some("codeBlock");

    Value::Object(
        map.into_iter()
            .filter_map(|(key, value)| {
                let value = match key.as_str() {
                    "attrs" if is_code_block => sanitize_code_block_attrs(value),
                    _ => sanitize_unused_code_block_attrs_class(value),
                };

                Some((key, value))
            })
            .collect(),
    )
}

fn sanitize_code_block_attrs(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| match key.as_str() {
                    "class" => None,
                    _ => Some((key, sanitize_unused_code_block_attrs_class(value))),
                })
                .collect(),
        ),
        _ => value,
    }
}
