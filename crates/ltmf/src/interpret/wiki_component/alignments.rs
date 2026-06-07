use serde_json::Value;

use crate::interpret::{
    text::interpret_text_content,
    utils::{
        get_attrs_text_align::get_attrs_text_align,
        get_intercepted_content::get_intercepted_content,
    },
};

pub(super) fn interpret_align_left(node: &Value, output: String) -> Result<String, String> {
    if !is_align_left(node) {
        return Ok(output);
    }

    let output = get_intercepted_content(node, interpret_text_content);

    Ok(format!("[[<]]\n{output}\n[[/<]]"))
}

pub(super) fn interpret_align_right(node: &Value, output: String) -> Result<String, String> {
    if !is_align_right(node) {
        return Ok(output);
    }

    let output = get_intercepted_content(node, interpret_text_content);

    Ok(format!("[[>]]\n{output}\n[[/>]]"))
}

pub(super) fn interpret_align_center(node: &Value, output: String) -> Result<String, String> {
    if !is_align_center(node) {
        return Ok(output);
    }

    let output = get_intercepted_content(node, interpret_text_content);

    Ok(format!("[[=]]\n{output}\n[[/=]]"))
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
