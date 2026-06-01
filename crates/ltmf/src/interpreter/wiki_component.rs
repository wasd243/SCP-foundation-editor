pub(crate) mod footnote;

use serde_json::Value;

use crate::interpreter::{
    utils::get_types::node_type, wiki_component::footnote::interpret_footnote,
};

pub fn interpret_wiki_component(index: usize, node: &Value) -> Result<String, String> {
    let node_type = expect_node_type(node)?;
    let content = interpret_footnote(node, String::new())?;

    Ok(format!("[wiki_component:{index}] {node_type} -> {content}"))
}

pub(crate) fn is_wiki_component_node(node: &Value) -> bool {
    matches!(
        node_type(node),
        Some("tabView" | "Collapsible" | "Note" | "Footnote")
    )
}

fn expect_node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "wiki component interpreter expected node type".to_string())
}
