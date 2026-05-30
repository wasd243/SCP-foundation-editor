use serde_json::Value;

use crate::preprocess::normalize::{
    normalize_details::normalize_details,
    normalize_footnote::normalize_footnote,
    normalize_hard_break::normalize_hard_break,
    normalize_note::normalize_note,
    normalize_new_line_marks::normalize_new_line_marks,
    normalize_strike::normalize_strike,
    normalize_white_space_pre_wrap::normalize_white_space_pre_wrap,
    normalize_tabview::normalize_tabview,
    // normalize_div::normalize_div,
};

pub mod normalize_details;
pub mod normalize_footnote;
pub mod normalize_hard_break;

pub mod normalize_new_line_marks;

pub mod normalize_strike;
pub mod normalize_white_space_pre_wrap;
pub mod rename;
pub mod normalize_tabview;
pub mod normalize_note;
// pub mod normalize_div;

pub fn normalize(value: Value) -> Value {
    // Normalize hard break to NewLine.
    let value = normalize_hard_break(value);
    let value = normalize_white_space_pre_wrap(value);
    let value = normalize_footnote(value);
    let value = normalize_strike(value);
    let value = normalize_details(value);
    let value = normalize_note(value);
    let value = normalize_tabview(value);
    // let value = normalize_div(value);
    normalize_new_line_marks(value)
}
