use serde_json::Value;

pub(super) fn normalize_div(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            let is_div = is_div_node(&Value::Object(map.clone()));

            if is_div {
                map.insert("type".to_string(), Value::String("Div".to_string()));
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, normalize_div(value)))
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(values.into_iter().map(normalize_div).collect()),
        _ => value,
    }
}

fn is_div_node(value: &Value) -> bool {
    value.get("type").and_then(Value::as_str) == Some("wjBlockTag")
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attrs| html_attrs.get("data-editor-export"))
            .and_then(Value::as_str)
            == Some("div")
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn normalizes_editor_export_div_to_div() {
        let value = json!({
            "type": "wjBlockTag",
            "attrs": {
                "tagName": "div",
                "htmlAttributes": {
                    "class": "test",
                    "data-editor-export": "div"
                }
            }
        });

        let normalized = normalize_div(value);

        assert_eq!(normalized.get("type").and_then(Value::as_str), Some("Div"));
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
    fn leaves_non_div_wj_block_tag_unchanged() {
        let value = json!({
            "type": "wjBlockTag",
            "attrs": {
                "htmlAttributes": {
                    "data-editor-export": "include"
                }
            }
        });

        let normalized = normalize_div(value);

        assert_eq!(
            normalized.get("type").and_then(Value::as_str),
            Some("wjBlockTag")
        );
    }
}
