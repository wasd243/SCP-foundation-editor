pub(crate) mod footnote;

use serde_json::Value;

use crate::interpreter::wiki_component::footnote::interpret_footnote;

pub fn interpret_wiki_component(index: usize, node: &Value) -> Result<String, String> {
    let node_type = node_type(node)?;
    let content = interpret_footnote(node, String::new())?;

    Ok(format!("[wiki_component:{index}] {node_type} -> {content}"))
}

fn node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "wiki component interpreter expected node type".to_string())
}
