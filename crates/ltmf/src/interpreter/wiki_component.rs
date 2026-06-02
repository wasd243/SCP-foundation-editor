mod alignments;
mod collapsible;
pub(crate) mod footnote;
mod tabview;

use serde_json::Value;

use crate::interpreter::{
    utils::get_types::node_type,
    wiki_component::{
        alignments::{
            interpret_align_center, interpret_align_left, interpret_align_right, is_align_center,
            is_align_left, is_align_right,
        },
        collapsible::interpret_collapsible,
        footnote::interpret_footnote,
        tabview::{interpret_tabview, is_tabview},
    },
};
pub fn interpret_wiki_component(index: usize, node: &Value) -> Result<String, String> {
    let node_type = expect_node_type(node)?;
    let content = interpret_footnote(node, String::new())?;
    let content = interpret_collapsible(node, content)?;
    let content = interpret_tabview(node, content)?;
    let content = interpret_align_left(node, content)?;
    let content = interpret_align_center(node, content)?;
    let content = interpret_align_right(node, content)?;

    Ok(format!("[wiki_component:{index}] {node_type} -> {content}"))
}

pub(crate) fn is_wiki_component_node(node: &Value) -> bool {
    is_align_left(node)
        || is_align_right(node)
        || is_align_center(node)
        || is_tabview(node)
        // This matches! macro only for identifier
        // Going to be removed for future implementation
        || matches!(node_type(node), Some("Collapsible" | "Note" | "Footnote"))
}

fn expect_node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "wiki component interpreter expected node type".to_string())
}
