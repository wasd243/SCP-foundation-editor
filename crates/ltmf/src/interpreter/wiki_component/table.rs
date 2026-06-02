use serde_json::Value;

use crate::interpreter::{
    text::interpret_text_content,
    utils::{get_intercepted_content::get_intercepted_content, get_types::has_type},
};

pub(super) fn interpret_table(node: &Value, output: String) -> Result<String, String> {
    if !is_table(node) {
        return Ok(output);
    }

    let output = node
        .get("content")
        .and_then(Value::as_array)
        .map(|rows| {
            rows.iter()
                .filter(|row| has_type(row, "tableRow"))
                .map(interpret_table_row)
                .collect::<Vec<_>>()
                .join("\n")
        })
        .unwrap_or_default();

    Ok(output)
}

pub(super) fn is_table(node: &Value) -> bool {
    has_type(node, "table")
}

fn interpret_table_row(node: &Value) -> String {
    node.get("content")
        .and_then(Value::as_array)
        .map(|cells| {
            let cells = cells.iter().map(interpret_table_cell).collect::<String>();
            format!("{cells}||")
        })
        .unwrap_or_else(|| "||".to_string())
}

fn interpret_table_cell(node: &Value) -> String {
    let content = get_intercepted_content(node, interpret_text_content);

    match table_cell_prefix(node) {
        Some(prefix) => format!("{prefix} {content} "),
        None => String::new(),
    }
}

fn table_cell_prefix(node: &Value) -> Option<&'static str> {
    if has_type(node, "tableHeader") {
        return Some("||~");
    }

    if has_type(node, "tableCell") {
        return Some("||");
    }

    None
}
