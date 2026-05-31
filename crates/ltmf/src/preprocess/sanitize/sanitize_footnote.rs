use serde_json::Value;

pub fn sanitize_footnote_refs(value: Value) -> Value {
    sanitize_value(value).unwrap_or(Value::Null)
}

fn sanitize_value(value: Value) -> Option<Value> {
    match value {
        Value::Object(map) => {
            let value = Value::Object(map);

            if has_html_class(&value, "wj-footnote-list") {
                return None;
            }

            if has_html_class(&value, "wj-footnote-ref") {
                return find_footnote_ref_contents(&value).map(sanitize_footnote_refs);
            }

            match value {
                Value::Object(map) => Some(Value::Object(
                    map.into_iter()
                        .filter_map(|(key, value)| sanitize_value(value).map(|value| (key, value)))
                        .collect(),
                )),
                _ => Some(value),
            }
        }
        Value::Array(values) => Some(Value::Array(
            values.into_iter().filter_map(sanitize_value).collect(),
        )),
        _ => Some(value),
    }
}

fn find_footnote_ref_contents(value: &Value) -> Option<Value> {
    if has_html_class(value, "wj-footnote-ref-contents") {
        return Some(value.clone());
    }

    match value {
        Value::Object(map) => map.values().find_map(find_footnote_ref_contents),
        Value::Array(values) => values.iter().find_map(find_footnote_ref_contents),
        _ => None,
    }
}

fn has_html_class(value: &Value, class_name: &str) -> bool {
    value
        .get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(|html_attributes| html_attributes.get("class"))
        .and_then(Value::as_str)
        .is_some_and(|class| class.split_whitespace().any(|class| class == class_name))
}
