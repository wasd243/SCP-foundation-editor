use serde_json::Value;

pub(crate) fn get_raw_text(node: &Value) -> String {
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
