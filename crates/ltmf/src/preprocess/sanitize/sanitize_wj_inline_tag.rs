use serde_json::Value;

/// Sanitize `wjInlineTag` function only sanitize the `type` field.
/// Because `wjInlineTag` is only used for TipTap/ProseMirror editor allowing ftml's customize HTML tags
pub fn sanitize_wj_inline_tag(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if key == "type" && value.as_str() == Some("wjInlineTag") {
                        None
                    } else {
                        Some((key, sanitize_wj_inline_tag(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => {
            Value::Array(values.into_iter().map(sanitize_wj_inline_tag).collect())
        }
        _ => value,
    }
}
