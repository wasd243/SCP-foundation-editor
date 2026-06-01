use serde_json::Value;

use crate::interpreter::utils::get_marks::has_mark;

pub fn interpret_sup_text(node: &Value, output: String) -> Result<String, String> {
    if !has_mark(node, "superscript") {
        return Ok(output);
    }

    Ok(format!("^^{output}^^"))
}
