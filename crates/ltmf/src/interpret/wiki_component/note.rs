use serde_json::Value;

use crate::interpret::{
    text::interpret_text_content,
    utils::{get_intercepted_content::get_intercepted_content, get_types::has_type},
};

pub(super) fn interpret_note(node: &Value, output: String) -> Result<String, String> {
    if !is_note(node) {
        return Ok(output);
    }

    let output = get_intercepted_content(node, interpret_text_content);

    Ok(format!("[[note]]\n{output}\n[[/note]]"))
}

pub(super) fn is_note(node: &Value) -> bool {
    has_type(node, "Note")
}
