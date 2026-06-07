use serde_json::Value;

use crate::interpret::utils::get_types::has_type;

pub(super) fn interpret_paragraph_with_contents(
    node: &Value,
    output: String,
) -> Result<String, String> {
    if !is_paragraph_with_contents(node) {
        return Ok(output);
    }

    Ok(format!("{output}\n\n"))
}

fn is_paragraph_with_contents(node: &Value) -> bool {
    has_type(node, "paragraph")
        && node
            .get("content")
            .and_then(Value::as_array)
            .map(|content| !content.is_empty())
            .unwrap_or(false)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn adds_two_newlines_to_paragraph_with_contents() {
        let node = json!({
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "content"
                }
            ]
        });

        assert_eq!(
            interpret_paragraph_with_contents(&node, "content".to_string()).unwrap(),
            "content\n\n"
        );
    }

    #[test]
    fn keeps_empty_paragraph_output() {
        let node = json!({
            "type": "paragraph"
        });

        assert_eq!(
            interpret_paragraph_with_contents(&node, "@@@@".to_string()).unwrap(),
            "@@@@"
        );
    }
}
