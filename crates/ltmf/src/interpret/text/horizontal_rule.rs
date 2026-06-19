use serde_json::Value;

use crate::interpret::utils::get_types::has_type;

pub(super) fn interpret_horizontal_rule(node: &Value, output: String) -> Result<String, String> {
    if !is_horizontal_rule(node) {
        return Ok(output);
    }

    let number_of_dashe = "-".repeat(50);

    Ok(format!("\n{number_of_dashe}\n"))
}

pub(super) fn is_horizontal_rule(node: &Value) -> bool {
    has_type(node, "HorizontalRule")
}
