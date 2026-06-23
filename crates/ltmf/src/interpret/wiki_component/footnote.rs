use serde_json::Value;
use crate::interpret::{text::interpret_wrapped_text_content, utils::get_types::has_type};

pub(super) fn interpret_footnote(node: &Value, output: String) -> Result<String, String> {
    if !has_type(node, "Footnote") {
        return Ok(output);
    }

    let output = interpret_wrapped_text_content(node, "Footnote");

    Ok(format!("[[footnote]]{output}[[/footnote]]"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn keeps_marks_inside_footnote() {
        let node = json!({
            "type": "Footnote",
            "content": [
                {
                    "type": "text",
                    "text": "plain "
                },
                {
                    "type": "text",
                    "marks": [{ "type": "bold" }],
                    "text": "bold"
                },
                {
                    "type": "text",
                    "marks": [{ "type": "italic" }],
                    "text": "italic"
                }
            ]
        });

        assert_eq!(
            interpret_footnote(&node, String::new()).unwrap(),
            "[[footnote]]plain **bold**//italic//[[/footnote]]"
        );
    }

    #[test]
    fn escapes_brackets_with_original_text() {
        let node = json!({
            "type": "Footnote",
            "content": [
                {
                    "type": "text",
                    "text": "see ]] here"
                }
            ]
        });

        assert_eq!(
            interpret_footnote(&node, String::new()).unwrap(),
            "[[footnote]]@@see ]] here@@[[/footnote]]"
        );
    }
}
