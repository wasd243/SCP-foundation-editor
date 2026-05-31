use serde_json::Value;

pub fn normalize_empty_paragraph_between_newline(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .map(|(key, value)| (key, normalize_empty_paragraph_between_newline(value)))
                .collect(),
        ),
        Value::Array(values) => normalize_array(values),
        _ => value,
    }
}

fn normalize_array(values: Vec<Value>) -> Value {
    let values: Vec<Value> = values
        .into_iter()
        .map(normalize_empty_paragraph_between_newline)
        .collect();

    let mut normalized = Vec::new();
    let mut index = 0;

    while index < values.len() {
        if index + 2 < values.len()
            && is_new_line(&values[index])
            && is_empty_paragraph(&values[index + 1])
            && is_new_line(&values[index + 2])
        {
            normalized.push(values[index + 1].clone());
            index += 3;
        } else {
            normalized.push(values[index].clone());
            index += 1;
        }
    }

    Value::Array(normalized)
}

fn is_new_line(value: &Value) -> bool {
    value.as_object().is_some_and(|map| {
        map.len() == 1 && map.get("type").and_then(Value::as_str) == Some("NewLine")
    })
}

fn is_empty_paragraph(value: &Value) -> bool {
    value.as_object().is_some_and(|map| {
        map.len() == 1 && map.get("type").and_then(Value::as_str) == Some("paragraph")
    })
}
