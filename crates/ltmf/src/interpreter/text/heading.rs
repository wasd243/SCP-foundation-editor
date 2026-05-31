use serde_json::Value;

pub fn interpret_heading(node: &Value, output: String) -> Result<String, String> {
    if node.get("type").and_then(Value::as_str) != Some("heading") {
        return Ok(output);
    }

    let level = node
        .get("attrs")
        .and_then(|attrs| attrs.get("level"))
        .and_then(Value::as_u64)
        .ok_or_else(|| "heading expected attrs.level".to_string())?;

    let text = heading_text(node);

    Ok(format!("{} {}", "+".repeat(level as usize), text))
}

fn heading_text(node: &Value) -> String {
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
