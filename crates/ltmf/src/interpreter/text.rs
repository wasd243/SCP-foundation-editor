mod bold;
pub(crate) mod color;
mod empty_paragraph;
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

use crate::interpreter::{
    text::{
        bold::interpret_bold_text, color::interpret_color_text,
        empty_paragraph::interpret_empty_paragraph, heading::interpret_heading,
        italic::interpret_italic_text, monospcae::interpret_monospace_text,
        new_line::interpret_new_line, normal_text::interpret_normal_text,
        original_text::interpret_original_text, strikethrough::interpret_strike_through_text,
        sub::interpret_sub_text, sup::interpret_sup_text, underline::interpret_underline_text,
    },
    utils::{
        get_content::{get_content_nodes, ContentNode},
        get_marks::get_marks,
        get_types::{has_type, node_type},
    },
    wiki_component::{interpret_wiki_component, is_wiki_component_node},
};

pub(super) fn interpret_text(index: usize, node: &Value) -> Result<String, String> {
    let node_type = expect_node_type(node)?;
    let content = interpret_text_content(node).join(", ");
    let content = interpret_heading(node, content)?;
    let content = interpret_normal_text(node, content)?;

    Ok(format!("[text:{index}] {node_type} -> {content}"))
}

pub(crate) fn interpret_text_content(node: &Value) -> Vec<String> {
    get_content_nodes(node, should_stop_collecting_children)
        .into_iter()
        .filter_map(interpret_content_node)
        .collect()
}

fn interpret_content_node(content_node: ContentNode<'_>) -> Option<String> {
    let node = content_node.node;

    match node_type(node) {
        Some("text") => Some(format!(
            "text:{}",
            interpret_text_node(node, content_node.parent_type)
                .unwrap_or_else(|error| format!("ERROR:{error}"))
        )),
        Some("NewLine") => Some(
            interpret_new_line(node, String::new())
                .unwrap_or_else(|error| format!("ERROR:{error}")),
        ),
        Some("paragraph") if is_empty_paragraph_node(node) => Some(
            interpret_empty_paragraph(node, String::new())
                .unwrap_or_else(|error| format!("ERROR:{error}")),
        ),
        Some(_) if is_wiki_component_node(node) => {
            Some(interpret_wiki_component(0, node).unwrap_or_else(|error| format!("ERROR:{error}")))
        }
        Some(node_type) => Some(format!("type:{node_type}")),
        None => None,
    }
}

fn should_stop_collecting_children(node: &Value) -> bool {
    is_empty_paragraph_node(node) || is_wiki_component_node(node)
}

fn is_empty_paragraph_node(node: &Value) -> bool {
    has_type(node, "paragraph")
        && node
            .get("content")
            .and_then(Value::as_array)
            .map(|content| content.is_empty())
            .unwrap_or(true)
}

fn interpret_text_node(node: &Value, parent_type: Option<&str>) -> Result<String, String> {
    let text = node
        .get("text")
        .and_then(Value::as_str)
        .ok_or_else(|| "text node expected text".to_string())?
        .to_string();

    let text = match get_marks(node).is_empty() {
        true => interpret_normal_text(node, text),
        false => interpret_marked_text(node, text),
    }?;

    match parent_type {
        Some("paragraph") => interpret_original_text(node, text),
        _ => Ok(text),
    }
}

/// Applies all mark-based inline text interpreters, such as color, bold,
/// italic, underline, and strikethrough.
fn interpret_marked_text(node: &Value, output: String) -> Result<String, String> {
    let output = interpret_color_text(node, output)?;
    let output = interpret_bold_text(node, output)?;
    let output = interpret_italic_text(node, output)?;
    let output = interpret_underline_text(node, output)?;
    let output = interpret_strike_through_text(node, output)?;
    let output = interpret_monospace_text(node, output)?;
    let output = interpret_sup_text(node, output)?;
    let output = interpret_sub_text(node, output)?;

    Ok(output)
}

fn expect_node_type(node: &Value) -> Result<&str, String> {
    node.get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "text interpreter expected node type".to_string())
}
