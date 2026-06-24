// This function removes unused footnote attrs.
// Also, it will add the type "footnote" to footnote ref contents.
use serde_json::Value;

pub(super) fn normalize_footnote(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let value = Value::Object(map);

            if is_footnote_ref_contents(&value) {
                return normalize_footnote_ref_contents(value);
            }

            match value {
                Value::Object(map) => Value::Object(
                    map.into_iter()
                        .map(|(key, value)| (key, normalize_footnote(value)))
                        .collect(),
                ),
                _ => value,
            }
        }
        Value::Array(values) => Value::Array(values.into_iter().map(normalize_footnote).collect()),
        _ => value,
    }
}

fn normalize_footnote_ref_contents(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let mut normalized = map
                .into_iter()
                .filter_map(|(key, value)| {
                    if key == "attrs" {
                        None
                    } else {
                        Some((key, normalize_footnote(value)))
                    }
                })
                .collect::<serde_json::Map<String, Value>>();

            normalized.insert("type".to_string(), Value::String("footnote".to_string()));
            Value::Object(normalized)
        }
        _ => value,
    }
}

fn is_footnote_ref_contents(value: &Value) -> bool {
    value
        .get("attrs")
        .and_then(|attrs| attrs.get("tagName"))
        .and_then(Value::as_str)
        == Some("span")
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attributes| html_attributes.get("class"))
            .and_then(Value::as_str)
            .is_some_and(|class| {
                class
                    .split_whitespace()
                    .any(|class| class == "wj-footnote-ref-contents")
            })
}
