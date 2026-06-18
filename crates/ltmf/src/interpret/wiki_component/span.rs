use serde_json::Value;

use crate::interpret::utils::get_attr_values::value_to_string;
use crate::interpret::{text::interpret_text_content, utils::get_types::has_type};

/// Interprets a Span node.
///
/// Unlike `[[div]]`, `[[span]]` is inline, so it is emitted on a single line
/// without surrounding newlines: `[[span attrs]]content[[/span]]`.
pub(super) fn interpret_span(node: &Value, output: String) -> Result<String, String> {
    if !is_span(node) {
        return Ok(output);
    }

    let span_attrs = span_attrs(node);
    let open_tag = match span_attrs.is_empty() {
        true => "[[span]]".to_string(),
        false => format!("[[span {span_attrs}]]"),
    };
    let content = span_content(node);

    Ok(format!("{open_tag}{content}[[/span]]"))
}

pub(super) fn is_span(node: &Value) -> bool {
    has_type(node, "Span")
}

/// Collects the inline content of a span node.
///
/// `interpret_text_content` cannot be called on the span node itself: because
/// the span is a nested wiki component, the content collector treats it as a
/// leaf and would re-route it back into `interpret_span`, recursing forever.
/// So we descend into the span's children directly, interpreting each as inline
/// text without surrounding newlines.
fn span_content(node: &Value) -> String {
    node.get("content")
        .and_then(Value::as_array)
        .map(|children| {
            children
                .iter()
                .map(|child| interpret_text_content(child).join(""))
                .collect::<String>()
        })
        .unwrap_or_default()
}

fn span_attrs(node: &Value) -> String {
    node.get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(Value::as_object)
        .map(|attrs| {
            attrs
                .iter()
                .filter_map(|(key, value)| span_attr(key, value))
                .collect::<Vec<_>>()
                .join(" ")
        })
        .unwrap_or_default()
}

fn span_attr(key: &str, value: &Value) -> Option<String> {
    if is_editor_attr(key) {
        return None;
    }

    let value = value_to_string(value)?;

    Some(format!("{key}=\"{value}\""))
}

fn is_editor_attr(key: &str) -> bool {
    key.starts_with("data-editor-") || matches!(key, "contenteditable" | "draggable")
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn interprets_span_with_attrs_and_inline_content() {
        let node = json!({
            "type": "Span",
            "attrs": {
                "tagName": "span",
                "htmlAttributes": {
                    "class": "test",
                    "data-editor-export": "span"
                }
            },
            "content": [
                {
                    "type": "text",
                    "text": "这是span测试文本test"
                }
            ]
        });

        assert_eq!(
            interpret_span(&node, String::new()).unwrap(),
            "[[span class=\"test\"]]这是span测试文本test[[/span]]"
        );
    }

    #[test]
    fn ignores_editor_attrs() {
        let node = json!({
            "type": "Span",
            "attrs": {
                "htmlAttributes": {
                    "class": "test",
                    "data-editor-export": "span",
                    "contenteditable": "true",
                    "draggable": "true"
                }
            }
        });

        assert_eq!(span_attrs(&node), "class=\"test\"");
    }
}
