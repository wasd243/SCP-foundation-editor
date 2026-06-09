use serde_json::Value;

use crate::interpret::{
    text::interpret_text_content,
    utils::{
        get_intercepted_content::get_intercepted_content,
        get_types::{has_type, node_type},
    },
};

pub(super) fn interpret_ol(node: &Value, output: String) -> Result<String, String> {
    if !is_ordered_list(node) {
        return Ok(output);
    }

    // What's wrong with this Agent...
    // I provided a function get_intercepted_content
    // It's just repeat it and import???
    // Maybe I should keep this because there's multiple listItem in ProseMirror JSON?
    // I hate Wikidot Lists
    let output = node
        .get("content")
        .and_then(Value::as_array)
        .map(|content| {
            content
                .iter()
                .filter(|node| has_type(node, "listItem"))
                .map(interpret_list_item)
                .collect::<Vec<_>>()
                .join("\n")
        })
        .unwrap_or_default();

    Ok(output)
}

pub(super) fn is_ordered_list(node: &Value) -> bool {
    matches!(node_type(node), Some("orderedList"))
}

fn interpret_list_item(node: &Value) -> String {
    let content = get_intercepted_content(node, interpret_text_content);

    format!("# {content}")
}
