use serde_json::Value;

fn sanitize_text_align_left(value: &Value) -> Value {
    sanitize_style(value, "text-align: left;")
}

fn sanitize_text_align_right(value: &Value) -> Value {
    sanitize_style(value, "text-align: right;")
}

fn sanitize_text_align_center(value: &Value) -> Value {
    sanitize_style(value, "text-align: center;")
}

fn sanitize_style(value: &Value, style: &str) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.iter()
                .filter_map(|(key, value)| {
                    if key == "style" && value.as_str() == Some(style) {
                        None
                    } else {
                        Some((key.clone(), sanitize_style(value, style)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(
            values
                .iter()
                .map(|value| sanitize_style(value, style))
                .collect(),
        ),
        _ => value.clone(),
    }
}

pub(super) fn sanitize_text_align(value: Value) -> Value {
    let value = sanitize_text_align_left(&value);
    let value = sanitize_text_align_center(&value);
    sanitize_text_align_right(&value)
}
