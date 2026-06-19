use serde_json::Value;

pub(super) fn normalize_span(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            let is_span = is_span_node(&Value::Object(map.clone()));

            if is_span {
                map.insert("type".to_string(), Value::String("Span".to_string()));
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, normalize_span(value)))
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(values.into_iter().map(normalize_span).collect()),
        _ => value,
    }
}

fn is_span_node(value: &Value) -> bool {
    value.get("type").and_then(Value::as_str) == Some("wjInlineTag")
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attrs| html_attrs.get("data-editor-export"))
            .and_then(Value::as_str)
            == Some("span")
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn normalizes_editor_export_span_to_span() {
        let value = json!({
            "type": "wjInlineTag",
            "attrs": {
                "tagName": "span",
                "htmlAttributes": {
                    "class": "test",
                    "data-editor-export": "span"
                }
            }
        });

        let normalized = normalize_span(value);

        assert_eq!(normalized.get("type").and_then(Value::as_str), Some("Span"));
        assert_eq!(
            normalized
                .get("attrs")
                .and_then(|attrs| attrs.get("htmlAttributes"))
                .and_then(|html_attrs| html_attrs.get("class"))
                .and_then(Value::as_str),
            Some("test")
        );
    }

    #[test]
    fn leaves_non_span_wj_inline_tag_unchanged() {
        let value = json!({
            "type": "wjInlineTag",
            "attrs": {
                "htmlAttributes": {
                    "data-editor-export": "include"
                }
            }
        });

        let normalized = normalize_span(value);

        assert_eq!(
            normalized.get("type").and_then(Value::as_str),
            Some("wjInlineTag")
        );
    }
}
