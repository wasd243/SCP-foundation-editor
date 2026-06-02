use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

pub fn normalize_bullet_list(value: Value) -> Value {
    rename_type(value, "bulletList", "unorderedList")
}
