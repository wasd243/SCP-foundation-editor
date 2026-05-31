use serde_json::Value;

pub fn identify_include(index: usize, node: &Value) -> Result<String, String> {
    let include_name = node
        .get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(|html_attrs| html_attrs.get("data-editor-include"))
        .and_then(Value::as_str)
        .unwrap_or("unknown");

    // PLACEHOLDER
    Ok(format!("[include:{index}] {include_name}"))
}
