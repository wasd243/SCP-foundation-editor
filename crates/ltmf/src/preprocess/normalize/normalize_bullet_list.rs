use serde_json::Value;
use crate::preprocess::normalize::rename::rename_type;

pub fn normalize_bullet_list(value: Value) -> Value {
    rename_type(value,"bulletList", "unorderedList")
}
