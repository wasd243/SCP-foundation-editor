use serde_json::Value;

/// This function only provides normal text output
pub fn interpret_normal_text(_node: &Value, output: String) -> Result<String, String> {
    Ok(output)
}
