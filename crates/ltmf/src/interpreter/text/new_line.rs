use serde_json::Value;

pub fn interpret_new_line(node: &Value, output: String) -> Result<String, String> {
    if crate::interpreter::get_types::has_type(node, "NewLine") {
        return Ok("\n".to_string());
    }

    Ok(output)
}
