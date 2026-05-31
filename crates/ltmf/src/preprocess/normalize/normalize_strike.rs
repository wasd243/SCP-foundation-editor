// This function will rename `strike` to `Strikethrough`
use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

pub fn normalize_strike(value: Value) -> Value {
    rename_type(value, "strike", "Strikethrough")
}
