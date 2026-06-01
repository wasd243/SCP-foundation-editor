use serde_json::Value;

use crate::interpreter::{text::interpret_text_content, utils::get_types::has_type};

pub fn interpret_footnote(node: &Value, output: String) -> Result<String, String> {
    if !has_type(node, "Footnote") {
        return Ok(output);
    }

    let output = node
        .get("content")
        .and_then(Value::as_array)
        .map(|content| {
            content
                .iter()
                .flat_map(interpret_text_content)
                .collect::<Vec<_>>()
                .join(", ")
        })
        .unwrap_or_default();

    Ok(format!("[[footnote]]{output}[[/footnote]]"))
}
