use serde_json::Value;

use crate::interpret::{text::patch_wiki_component_content, utils::get_types::has_type};

pub(super) fn interpret_note(node: &Value, output: String) -> Result<String, String> {
    if !is_note(node) {
        return Ok(output);
    }

    let output = patch_wiki_component_content(node)?;

    Ok(format!("[[note]]\n{output}\n[[/note]]\n"))
}

pub(super) fn is_note(node: &Value) -> bool {
    has_type(node, "Note")
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn parses_paragraph_inside_note() {
        let node = json!({
            "type": "Note",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "note content"
                        }
                    ]
                }
            ]
        });

        assert_eq!(
            interpret_note(&node, String::new()).unwrap(),
            "[[note]]\nnote content\n[[/note]]\n"
        );
    }
}
