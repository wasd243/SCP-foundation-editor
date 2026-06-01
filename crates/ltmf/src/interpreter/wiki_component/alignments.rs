use serde_json::Value;

use crate::interpreter::{
    text::interpret_text_content, utils::get_intercepted_content::get_intercepted_content,
};

pub fn interpret_align_left(node: &Value, output: String) -> Result<String, String> {
    if !is_align_left(node) {
        return Ok(output);
    }

    let output = get_intercepted_content(node, interpret_text_content);

    Ok(format!("[[<]]\n{output}\n[[/<]]"))
}

pub fn interpret_align_right(node: &Value, output: String) -> Result<String, String> {
    if !is_align_right(node) {
        return Ok(output);
    }
    let output = get_intercepted_content(node, interpret_text_content);

    Ok(format!("[[>]]\n{output}\n[[/>]]"))
}

pub(crate) fn is_align_left(node: &Value) -> bool {
    node.get("attrs")
        .and_then(|attrs| attrs.get("textAlign"))
        .and_then(Value::as_str)
        == Some("left")
}

pub(crate) fn is_align_right(node: &Value) -> bool {
    node.get("attrs")
        .and_then(|attrs| attrs.get("textAlign"))
        .and_then(Value::as_str)
        == Some("right")
}
