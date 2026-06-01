use serde_json::Value;

use crate::interpreter::get_types::has_type;

pub fn interpret_original_text(node: &Value, output: String) -> Result<String, String> {
    if !is_original_text_node(node) {
        return Ok(output);
    }

    Ok(format!("@@{output}@@"))
}

fn is_original_text_node(node: &Value) -> bool {
    has_type(node, "text")
        && node
            .get("text")
            .and_then(Value::as_str)
            .is_some_and(|text| text.starts_with("[[") || text.contains("]]"))
}
