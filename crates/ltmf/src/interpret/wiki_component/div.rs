use serde_json::Value;

use crate::interpret::utils::get_attr_values::value_to_string;
use crate::interpret::{text::patch_wiki_component_content, utils::get_types::has_type};

/// Interprets a Div node.
pub(super) fn interpret_div(node: &Value, output: String) -> Result<String, String> {
    if !is_div(node) {
        return Ok(output);
    }

    let div_attrs = div_attrs(node);
    let open_tag = match div_attrs.is_empty() {
        true => "[[div]]".to_string(),
        false => format!("[[div {div_attrs}]]"),
    };
    let output = patch_wiki_component_content(node)?;

    match output.is_empty() {
        true => Ok(format!("{open_tag}\n[[/div]]\n")),
        false => Ok(format!("{open_tag}\n{output}\n[[/div]]\n")),
    }
}

pub(super) fn is_div(node: &Value) -> bool {
    has_type(node, "Div")
}

fn div_attrs(node: &Value) -> String {
    node.get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(Value::as_object)
        .map(|attrs| {
            attrs
                .iter()
                .filter_map(|(key, value)| div_attr(key, value))
                .collect::<Vec<_>>()
                .join(" ")
        })
        .unwrap_or_default()
}

fn div_attr(key: &str, value: &Value) -> Option<String> {
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
    fn interprets_div_with_attrs_and_paragraph_content() {
        let node = json!({
            "type": "Div",
            "attrs": {
                "tagName": "div",
                "htmlAttributes": {
                    "class": "test",
                    "data-editor-export": "div"
                }
            },
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a test 这是div测试文本test"
                        }
                    ]
                }
            ]
        });

        assert_eq!(
            interpret_div(&node, String::new()).unwrap(),
            "[[div class=\"test\"]]\nThis is a test 这是div测试文本test\n[[/div]]\n"
        );
    }

    #[test]
    fn ignores_editor_attrs() {
        let node = json!({
            "type": "Div",
            "attrs": {
                "htmlAttributes": {
                    "class": "test",
                    "data-editor-export": "div",
                    "contenteditable": "true",
                    "draggable": "true"
                }
            }
        });

        assert_eq!(div_attrs(&node), "class=\"test\"");
    }
}
