use serde_json::Value;

use crate::interpreter::utils::get_types::has_type;

pub(super) fn interpret_empty_paragraph(node: &Value, output: String) -> Result<String, String> {
    if !is_empty_paragraph(node) {
        return Ok(output);
    }

    // add `\n` before `@@@@`
    Ok("@@@@".to_string())
}

fn is_empty_paragraph(node: &Value) -> bool {
    if !has_type(node, "paragraph") {
        return false;
    }

    node.get("content")
        .and_then(Value::as_array)
        .map(|content| content.is_empty())
        .unwrap_or(true)
}
