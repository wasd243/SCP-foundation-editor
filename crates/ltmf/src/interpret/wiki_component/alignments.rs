use serde_json::Value;

use crate::interpret::{
    text::{patch_wiki_component_text, trim_trailing_newlines},
    utils::get_attrs_text_align::get_attrs_text_align,
};

pub(super) fn interpret_align_left(node: &Value, output: String) -> Result<String, String> {
    if !is_align_left(node) {
        return Ok(output);
    }

    let output = trim_trailing_newlines(patch_wiki_component_text(node)?);

    Ok(format!("[[<]]\n{output}\n[[/<]]\n"))
}

pub(super) fn interpret_align_right(node: &Value, output: String) -> Result<String, String> {
    if !is_align_right(node) {
        return Ok(output);
    }

    let output = trim_trailing_newlines(patch_wiki_component_text(node)?);

    Ok(format!("[[>]]\n{output}\n[[/>]]\n"))
}

pub(super) fn interpret_align_center(node: &Value, output: String) -> Result<String, String> {
    if !is_align_center(node) {
        return Ok(output);
    }

    let output = trim_trailing_newlines(patch_wiki_component_text(node)?);

    Ok(format!("[[=]]\n{output}\n[[/=]]\n"))
}

pub(super) fn is_align_left(node: &Value) -> bool {
    get_attrs_text_align(node, "left")
}

pub(super) fn is_align_right(node: &Value) -> bool {
    get_attrs_text_align(node, "right")
}

pub(super) fn is_align_center(node: &Value) -> bool {
    get_attrs_text_align(node, "center")
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn wraps_aligned_paragraph_after_paragraph_patch() {
        let node = json!({
            "type": "paragraph",
            "attrs": {
                "textAlign": "right"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Aligned content"
                }
            ]
        });

        assert_eq!(
            interpret_align_right(&node, String::new()).unwrap(),
            "[[>]]\nAligned content\n[[/>]]\n"
        );
    }
}
