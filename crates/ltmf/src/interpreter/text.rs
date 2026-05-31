mod get_content;

use serde_json::Value;

use crate::interpreter::text::get_content::get_content;

pub fn identify_text(index: usize, node: &Value) -> Result<String, String> {
    let node_type = node_type(node)?;
    let content = get_content(node).join(", ");

    Ok(format!("[text:{index}] {node_type} -> {content}"))
}

fn node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "text interpreter expected node type".to_string())
}
