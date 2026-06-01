use serde_json::Value;

use crate::interpreter::utils::get_marks::has_mark;

pub fn interpret_bold_text(node: &Value, output: String) -> Result<String, String> {
    if !has_mark(node, "bold") {
        return Ok(output);
    }

    Ok(format!("**{output}**"))
}
