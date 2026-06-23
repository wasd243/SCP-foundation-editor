use serde_json::Value;

use crate::interpret::utils::get_types::node_type;

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

/// Collects the content nodes of `node`'s children while attributing
/// `parent_type` to those direct children.
///
/// Unlike [`get_content_nodes`], the wrapper `node` itself is not emitted, so
/// inline wrapper components (e.g. footnotes) can interpret their children with
/// the wrapper as the parent type without re-entering the wrapper.
pub(crate) fn get_child_content_nodes<'a, F>(
    node: &'a Value,
    parent_type: Option<&'a str>,
    should_stop: F,
) -> Vec<ContentNode<'a>>
where
    F: Fn(&Value) -> bool,
{
    let mut content = Vec::new();
    if let Some(values) = node.get("content").and_then(Value::as_array) {
        for value in values {
            collect_content(value, &mut content, parent_type, &should_stop);
        }
    }
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
