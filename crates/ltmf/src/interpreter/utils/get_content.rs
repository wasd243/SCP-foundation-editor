use serde_json::Value;

use crate::interpreter::utils::get_types::node_type;

pub struct ContentNode<'a> {
    pub node: &'a Value,
    pub parent_type: Option<&'a str>,
}

pub(crate) fn get_content_nodes<F>(node: &Value, should_stop: F) -> Vec<ContentNode<'_>>
where
    F: Fn(&Value) -> bool,
{
    let mut content = Vec::new();
    collect_content(node, &mut content, None, &should_stop);
    content
}

fn collect_content<'a, F>(
    node: &'a Value,
    content: &mut Vec<ContentNode<'a>>,
    parent_type: Option<&'a str>,
    should_stop: &F,
) where
    F: Fn(&Value) -> bool,
{
    match node {
        Value::Object(map) => {
            let current_type = node_type(node);

            if current_type.is_some() {
                content.push(ContentNode { node, parent_type });
            }

            if should_stop(node) {
                return;
            }

            if let Some(values) = map.get("content").and_then(Value::as_array) {
                for value in values {
                    collect_content(value, content, current_type, should_stop);
                }
            }
        }
        Value::Array(values) => {
            for value in values {
                collect_content(value, content, parent_type, should_stop);
            }
        }
        _ => {}
    }
}
