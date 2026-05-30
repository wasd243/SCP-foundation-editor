use serde_json::Value;

use crate::preprocess::normalize::{
    normalize_hard_break::normalize_hard_break
};

pub mod normalize_hard_break;

pub fn normalize(value: Value) -> Value {
    // Normalize hard break to NewLine.
    normalize_hard_break(value)
}
