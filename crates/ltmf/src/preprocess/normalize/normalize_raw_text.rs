use serde_json::Value;

pub fn normalize_raw_text(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let value = Value::Object(map);

            if let Some(text) = raw_text(&value) {
                return serde_json::json!({
                    "text": text,
                    "type": "text"
                });
            }

            match value {
                Value::Object(map) => Value::Object(
                    map.into_iter()
                        .map(|(key, value)| (key, normalize_raw_text(value)))
                        .collect(),
                ),
                _ => value,
            }
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(normalize_raw_text)
                .collect(),
        ),
        _ => value,
    }
}

fn raw_text(value: &Value) -> Option<String> {
    if !is_pre_wrap_span(value) {
        return None;
    }

    let content = value.get("content")?.as_array()?;
    let mut text = String::new();

    for item in content {
        if item.get("type").and_then(Value::as_str) != Some("text") {
            return None;
        }

        text.push_str(item.get("text")?.as_str()?);
    }

    Some(text)
}

fn is_pre_wrap_span(value: &Value) -> bool {
    value
        .get("attrs")
        .and_then(|attrs| attrs.get("tagName"))
        .and_then(Value::as_str)
        == Some("span")
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attrs| html_attrs.get("style"))
            .and_then(Value::as_str)
            == Some("white-space: pre-wrap;")
}
