use serde_json::Value;

pub(crate) fn get_attrs_text_align(node: &Value, align: &str) -> bool {
    node.get("attrs")
        .and_then(|attrs| attrs.get("textAlign"))
        .and_then(Value::as_str)
        == Some(align)
}
