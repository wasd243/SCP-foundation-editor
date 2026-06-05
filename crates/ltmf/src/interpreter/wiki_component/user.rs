use serde_json::Value;

use crate::interpreter::utils::get_types::has_type;

pub(super) fn interpret_user(node: &Value, output: String) -> Result<String, String> {
    if !is_user(node) {
        return Ok(output);
    }

    let user = user_name(node).ok_or_else(|| "user expected attrs.user".to_string())?;

    if has_type(node, "userWithImg") {
        return Ok(format!("[[*user {user}]]"));
    }

    Ok(format!("[[user {user}]]"))
}

pub(super) fn is_user(node: &Value) -> bool {
    has_type(node, "user") || has_type(node, "userWithImg")
}

fn user_name(node: &Value) -> Option<&str> {
    node.get("attrs")?.get("user")?.as_str()
}
