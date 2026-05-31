use serde_json::Value;

pub fn identify_text(index: usize, node: &Value) -> Result<String, String> {
    let node_type = node_type(node)?;
    Ok(format!("[text:{index}] {node_type}"))
}

fn node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "text identify expected node type".to_string())
}
