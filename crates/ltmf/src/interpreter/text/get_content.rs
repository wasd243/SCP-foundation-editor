use serde_json::Value;

use crate::interpreter::{
    get_marks::get_marks,
    get_types::node_type,
    text::{
        bold::interpret_bold_text, color::interpret_color_text, new_line::interpret_new_line,
        normal_text::interpret_normal_text, italic::interpret_italic_text, underline::interpret_underline_text,
    },
};

pub fn get_content(node: &Value) -> Vec<String> {
    let mut content = Vec::new();
    collect_content(node, &mut content);
    content
}

fn collect_content(node: &Value, content: &mut Vec<String>) {
    match node {
        Value::Object(map) => {
            match node_type(node) {
                Some("text") => {
                    let text =
                        interpret_text_node(node).unwrap_or_else(|error| format!("ERROR:{error}"));
                    content.push(format!("text:{text}"));
                }
                Some("NewLine") => {
                    let new_line = interpret_new_line(node, String::new())
                        .unwrap_or_else(|error| format!("ERROR:{error}"));
                    content.push(new_line);
                }
                Some(node_type) => content.push(format!("type:{node_type}")),
                None => {}
            }

            if let Some(values) = map.get("content").and_then(Value::as_array) {
                for value in values {
                    collect_content(value, content);
                }
            }
        }
        Value::Array(values) => {
            for value in values {
                collect_content(value, content);
            }
        }
        _ => {}
    }
}

fn interpret_text_node(node: &Value) -> Result<String, String> {
    let text = node
        .get("text")
        .and_then(Value::as_str)
        .ok_or_else(|| "text node expected text".to_string())?
        .to_string();

    match get_marks(node).is_empty() {
        true => interpret_normal_text(node, text),
        false => interpret_marked_text(node, text),
    }
}

/// ALL marked text like bold, italic, underline, strikethrough, etc. Should be placed in here.
fn interpret_marked_text(node: &Value, output: String) -> Result<String, String> {
    let output = interpret_color_text(node, output)?;
    let output = interpret_bold_text(node, output)?;
    let output = interpret_italic_text(node, output)?;
    let output = interpret_underline_text(node, output)?;

    Ok(output)
}
