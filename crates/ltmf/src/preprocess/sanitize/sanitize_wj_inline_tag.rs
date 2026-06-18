use serde_json::Value;

/// Sanitize `wjInlineTag` function only sanitize the `type` field.
/// Because `wjInlineTag` is only used for TipTap/ProseMirror editor allowing ftml's customize HTML tags
///
/// Exception: inline tags carrying `data-editor-export="span"` are kept intact so
/// `normalize_span` can later promote them to `Span` nodes for the exporter.
pub(super) fn sanitize_wj_inline_tag(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let preserve = is_export_span(&map);

            Value::Object(
                map.into_iter()
                    .filter_map(|(key, value)| {
                        if !preserve && key == "type" && value.as_str() == Some("wjInlineTag") {
                            None
                        } else {
                            Some((key, sanitize_wj_inline_tag(value)))
                        }
                    })
                    .collect(),
            )
        }
        Value::Array(values) => {
            Value::Array(values.into_iter().map(sanitize_wj_inline_tag).collect())
        }
        _ => value,
    }
}

fn is_export_span(map: &serde_json::Map<String, Value>) -> bool {
    map.get("type").and_then(Value::as_str) == Some("wjInlineTag")
        && map
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
    fn strips_type_of_plain_inline_tag() {
        let value = json!({
            "type": "wjInlineTag",
            "attrs": {
                "tagName": "span",
                "htmlAttributes": {}
            }
        });

        let sanitized = sanitize_wj_inline_tag(value);

        assert_eq!(sanitized.get("type"), None);
    }

    #[test]
    fn keeps_type_of_export_span_inline_tag() {
        let value = json!({
            "type": "wjInlineTag",
            "attrs": {
                "tagName": "span",
                "htmlAttributes": {
                    "data-editor-export": "span"
                }
            }
        });

        let sanitized = sanitize_wj_inline_tag(value);

        assert_eq!(
            sanitized.get("type").and_then(Value::as_str),
            Some("wjInlineTag")
        );
    }
}
