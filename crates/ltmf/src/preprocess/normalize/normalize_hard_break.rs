// This function will rename `hardBreak` to `NewLine`
use serde_json::Value;
use crate::preprocess::normalize::rename::rename_type;

pub fn normalize_hard_break(value: Value) -> Value {
    rename_type(value, "hardBreak", "NewLine")
}
