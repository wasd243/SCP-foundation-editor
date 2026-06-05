use serde_json::Value;

pub(crate) fn get_intercepted_content<F>(node: &Value, interpret_content: F) -> String
where
    F: Fn(&Value) -> Vec<String>,
{
    node.get("content")
        .and_then(Value::as_array)
        .map(|content| {
            content
                .iter()
                .flat_map(interpret_content)
                .collect::<Vec<_>>()
                .join("")
        })
        .unwrap_or_default()
}
