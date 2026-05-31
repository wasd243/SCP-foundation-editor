use serde_json::Value;

pub fn interpret_wiki_component(index: usize, node: &Value) -> Result<String, String> {
    let node_type = node_type(node)?;
    Ok(format!("[wiki_component:{index}] {node_type}"))
}

fn node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "wiki component interpreter expected node type".to_string())
}
