use serde_json::Value;

use crate::interpreter::{
    text::interpret_text_content,
    utils::{
        get_intercepted_content::get_intercepted_content,
        get_types::{has_type, node_type},
    },
};

pub(super) fn interpret_blockquote(node: &Value, output: String) -> Result<String, String> {
    if !is_blockquote(node) {
        return Ok(output);
    }

    let output = node
        .get("content")
        .and_then(Value::as_array)
        .map(|content| {
            content
                .iter()
                .map(interpret_blockquote_content)
                .collect::<Vec<_>>()
                .join("\n")
        })
        .unwrap_or_default();

    Ok(output)
}

pub(super) fn is_blockquote(node: &Value) -> bool {
    matches!(node_type(node), Some("blockquote"))
}

fn interpret_blockquote_content(node: &Value) -> String {
    let content = match has_type(node, "paragraph") {
        true => get_intercepted_content(node, interpret_text_content),
        false => interpret_text_content(node).join(", "),
    };

    quote_lines(&content)
}

fn quote_lines(content: &str) -> String {
    content
        .lines()
        .map(|line| format!("> {line}"))
        .collect::<Vec<_>>()
        .join("\n")
}
