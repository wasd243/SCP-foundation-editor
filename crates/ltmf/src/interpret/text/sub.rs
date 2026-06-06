use serde_json::Value;

use crate::interpret::utils::get_marks::has_mark;

pub(super) fn interpret_sub_text(node: &Value, output: String) -> Result<String, String> {
    if !has_mark(node, "subscript") {
        return Ok(output);
    }

    Ok(format!(",,{output},,"))
}
