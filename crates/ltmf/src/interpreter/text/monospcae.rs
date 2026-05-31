use serde_json::Value;

use crate::interpreter::get_marks::has_mark;

pub fn interpret_monospace_text(node: &Value, output: String) -> Result<String, String> {
    if !has_mark(node, "code") {
        return Ok(output);
    }

    Ok(format!("{{{{{output}}}}}"))
}
