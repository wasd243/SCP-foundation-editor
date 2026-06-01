mod bold;
pub mod color;
mod empty_paragraph;
mod interpret_content;
mod heading;
mod italic;
mod monospcae;
mod new_line;
mod normal_text;
mod original_text;
mod strikethrough;
mod sub;
mod sup;
mod underline;

use serde_json::Value;

use crate::interpreter::text::{
    interpret_content::interpret_text_content, heading::interpret_heading, normal_text::interpret_normal_text,
};

pub fn interpret_text(index: usize, node: &Value) -> Result<String, String> {
    let node_type = node_type(node)?;
    let content = interpret_text_content(node).join(", ");
    let content = interpret_heading(node, content)?;
    let content = interpret_normal_text(node, content)?;

    Ok(format!("[text:{index}] {node_type} -> {content}"))
}

fn node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "text interpreter expected node type".to_string())
}
