pub mod color;
mod get_content;
mod heading;
mod new_line;
mod normal_text;

use serde_json::Value;

use crate::interpreter::text::{
    get_content::get_content, heading::interpret_heading, normal_text::interpret_normal_text,
};

pub fn interpret_text(index: usize, node: &Value) -> Result<String, String> {
    let node_type = node_type(node)?;
    let content = get_content(node).join(", ");
    let content = interpret_heading(node, content)?;
    let content = interpret_normal_text(node, content)?;

    Ok(format!("[text:{index}] {node_type} -> {content}"))
}

fn node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "text interpreter expected node type".to_string())
}
