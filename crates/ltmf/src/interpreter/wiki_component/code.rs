use serde_json::Value;

use crate::interpreter::utils::get_types::has_type;

pub(super) fn interpret_code(node: &Value, output: String) -> Result<String, String> {
    if !is_code(node) {
        return Ok(output);
    }

    let content = raw_text_content(node);

    match code_language(node) {
        Some(language) => Ok(format!(
            "[[code type=\"{language}\"]]\n{content}\n[[/code]]"
        )),
        None => Ok(format!("[[code]]\n{content}\n[[/code]]")),
    }
}

pub(super) fn is_code(node: &Value) -> bool {
    has_type(node, "codeBlock")
}

fn code_language(node: &Value) -> Option<&str> {
    node.get("attrs")?.get("language")?.as_str()
}

fn raw_text_content(node: &Value) -> String {
    node.get("content")
        .and_then(Value::as_array)
        .map(|content| {
            content
                .iter()
                .filter_map(|node| node.get("text").and_then(Value::as_str))
                .collect::<String>()
        })
        .unwrap_or_default()
}
