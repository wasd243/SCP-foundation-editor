// This function will rename `hardBreak` to `NewLine`
use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

pub(super) fn normalize_hard_break(value: Value) -> Value {
    rename_type(value, "hardBreak", "NewLine")
}
