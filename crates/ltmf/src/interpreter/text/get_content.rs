use serde_json::Value;

use crate::interpreter::text::{color::interpret_color_text, normal_text::interpret_normal_text};

pub fn get_content(node: &Value) -> Vec<String> {
    let mut content = Vec::new();
    collect_content(node, &mut content);
    content
}

fn collect_content(node: &Value, content: &mut Vec<String>) {
    match node {
        Value::Object(map) => {
            match map.get("type").and_then(Value::as_str) {
                Some("text") => {
                    let text =
                        interpret_text_node(node).unwrap_or_else(|error| format!("ERROR:{error}"));
                    content.push(format!("text:{text}"));
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

    match node.get("marks") {
        Some(_) => interpret_marked_text(node, text),
        None => interpret_normal_text(node, text),
    }
}

fn interpret_marked_text(node: &Value, output: String) -> Result<String, String> {
    let output = interpret_color_text(node, output)?;

    Ok(output)
}
