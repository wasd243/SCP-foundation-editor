use serde_json::Value;

use crate::preprocess::normalize::{
    normalize_bullet_list::normalize_bullet_list,
    normalize_color_text_marks::normalize_color_text_marks,
    normalize_details::normalize_details,
    normalize_empty_paragraph_between_newline::normalize_empty_paragraph_between_newline,
    normalize_footnote::normalize_footnote,
    normalize_force_new_line::normalize_force_new_line_to_paragraph,
    normalize_hard_break::normalize_hard_break,
    // normalize_div::normalize_div,
    normalize_horizontalrule::normalize_horizontalrule,
    normalize_include::normalize_include,
    normalize_new_line_marks::normalize_new_line_marks,
    normalize_note::normalize_note,
    normalize_raw_text::normalize_raw_text,
    normalize_strike::normalize_strike,
    normalize_tabview::normalize_tabview,
    normalize_white_space_pre_wrap::normalize_white_space_pre_wrap,
    normalize_font_size::normalize_font_size,
};

mod normalize_bullet_list;
mod normalize_color_text_marks;
mod normalize_details;
mod normalize_empty_paragraph_between_newline;
mod normalize_footnote;
mod normalize_force_new_line;
mod normalize_hard_break;
mod normalize_horizontalrule;
mod normalize_include;
mod normalize_new_line_marks;
mod normalize_note;
mod normalize_raw_text;
mod normalize_strike;
mod normalize_tabview;
mod normalize_white_space_pre_wrap;
pub mod rename;
mod normalize_font_size;
// pub mod normalize_div;

pub fn normalize(value: Value) -> Value {
    // Normalize hard break to NewLine.
    let value = normalize_hard_break(value);

    // This function normalizes `WhiteSpacePreWrap` to `ForceNewLine`.
    let value = normalize_white_space_pre_wrap(value);

    let value = normalize_raw_text(value);
    let value = normalize_footnote(value);
    let value = normalize_color_text_marks(value);
    let value = normalize_strike(value);
    let value = normalize_details(value);
    let value = normalize_note(value);
    let value = normalize_include(value);
    let value = normalize_tabview(value);
    let value = normalize_horizontalrule(value);
    let value = normalize_bullet_list(value);
    let value = normalize_font_size(value);

    // This function normalizes `ForceNewLine` to `Paragraph`.
    let value = normalize_force_new_line_to_paragraph(value);

    // Normalize empty paragraph between `NewLine` to a signal `NewLine`.
    let value = normalize_empty_paragraph_between_newline(value);

    // let value = normalize_div(value);
    normalize_new_line_marks(value)
}
