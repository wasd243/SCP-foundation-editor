use serde_json::Value;

pub fn get_types(node: &Value) -> Vec<&str> {
    let mut types = Vec::new();
    collect_types(node, &mut types);
    types
}

pub fn node_type(node: &Value) -> Option<&str> {
    node.get("type").and_then(Value::as_str)
}

pub fn has_type(node: &Value, expected_type: &str) -> bool {
    node_type(node) == Some(expected_type)
}

pub fn contains_type(node: &Value, expected_type: &str) -> bool {
    get_types(node)
        .into_iter()
        .any(|node_type| node_type == expected_type)
}

fn collect_types<'a>(node: &'a Value, types: &mut Vec<&'a str>) {
    match node {
        Value::Object(map) => {
            if let Some(node_type) = map.get("type").and_then(Value::as_str) {
                types.push(node_type);
            }

            for value in map.values() {
                collect_types(value, types);
            }
        }
        Value::Array(values) => {
            for value in values {
                collect_types(value, types);
            }
        }
        _ => {}
    }
}
