use serde_json::Value;

pub fn get_content(node: &Value) -> Vec<String> {
    let mut content = Vec::new();
    collect_content(node, &mut content);
    content
}

fn collect_content(node: &Value, content: &mut Vec<String>) {
    match node {
        Value::Object(map) => {
            if let Some(text) = map.get("text").and_then(Value::as_str) {
                content.push(format!("text:{text}"));
            } else if let Some(node_type) = map.get("type").and_then(Value::as_str) {
                content.push(format!("type:{node_type}"));
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
