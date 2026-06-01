use serde_json::Value;

use crate::interpreter::text::{
    bold::interpret_bold_text, color::interpret_color_text,
    empty_paragraph::interpret_empty_paragraph, italic::interpret_italic_text,
    monospcae::interpret_monospace_text, new_line::interpret_new_line,
    normal_text::interpret_normal_text, original_text::interpret_original_text,
    strikethrough::interpret_strike_through_text, sub::interpret_sub_text,
    sup::interpret_sup_text, underline::interpret_underline_text,
};
use crate::interpreter::utils::get_marks::get_marks;
use crate::interpreter::utils::get_types::node_type;

pub fn get_content(node: &Value) -> Vec<String> {
    let mut content = Vec::new();
    collect_content(node, &mut content, None);
    content
}

fn collect_content(node: &Value, content: &mut Vec<String>, parent_type: Option<&str>) {
    match node {
        Value::Object(map) => {
            let current_type = node_type(node);

            match current_type {
                Some("text") => {
                    let text = interpret_text_node(node, parent_type)
                        .unwrap_or_else(|error| format!("ERROR:{error}"));
                    content.push(format!("text:{text}"));
                }
                Some("NewLine") => {
                    let new_line = interpret_new_line(node, String::new())
                        .unwrap_or_else(|error| format!("ERROR:{error}"));
                    content.push(new_line);
                }
                Some("paragraph") if is_empty_paragraph_node(node) => {
                    let empty_paragraph = interpret_empty_paragraph(node, String::new())
                        .unwrap_or_else(|error| format!("ERROR:{error}"));
                    content.push(empty_paragraph);
                }
                Some(node_type) => content.push(format!("type:{node_type}")),
                None => {}
            }

            if !is_empty_paragraph_node(node) {
                if let Some(values) = map.get("content").and_then(Value::as_array) {
                    for value in values {
                        collect_content(value, content, current_type);
                    }
                }
            }
        }
        Value::Array(values) => {
            for value in values {
                collect_content(value, content, parent_type);
            }
        }
        _ => {}
    }
}

fn is_empty_paragraph_node(node: &Value) -> bool {
    node_type(node) == Some("paragraph")
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
