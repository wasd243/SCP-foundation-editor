use serde_json::Value;

use crate::interpret::utils::get_types::has_type;

pub(super) fn interpret_horizontal_rule(node: &Value, output: String) -> Result<String, String> {
    if !is_horizontal_rule(node) {
        return Ok(output);
    }

    Ok("-".repeat(50))
}

pub(super) fn is_horizontal_rule(node: &Value) -> bool {
    has_type(node, "HorizontalRule")
}
