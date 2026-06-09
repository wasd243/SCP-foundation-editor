use serde_json::Value;

use crate::interpret::utils::get_marks::has_mark;

pub(super) fn interpret_strike_through_text(
    node: &Value,
    output: String,
) -> Result<String, String> {
    if !has_mark(node, "Strikethrough") {
        return Ok(output);
    }

    Ok(format!("--{output}--"))
}
