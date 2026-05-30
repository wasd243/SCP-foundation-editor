// This function will remove note json attrs and change the type to Note
use serde_json::Value;

pub fn normalize_note(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            let is_note = is_note_node(&Value::Object(map.clone()));

            if is_note {
                map.remove("attrs");
                map.insert("type".to_string(), Value::String("Note".to_string()));
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, normalize_note(value)))
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(normalize_note)
                .collect(),
        ),
        _ => value,
    }
}

fn is_note_node(value: &Value) -> bool {
    value.get("type").and_then(Value::as_str) == Some("wjBlockTag")
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attrs| html_attrs.get("class"))
            .and_then(Value::as_str)
            == Some("wj-note")
}
