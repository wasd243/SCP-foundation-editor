use serde_json::Value;

use crate::preprocess::normalize::{
    normalize_hard_break::normalize_hard_break,
    normalize_strike::normalize_strike,
};

pub mod normalize_hard_break;
pub mod normalize_strike;
pub mod rename;

pub fn normalize(value: Value) -> Value {
    // Normalize hard break to NewLine.
    let value = normalize_hard_break(value);
    normalize_strike(value)
}
