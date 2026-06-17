mod add_footnote_block;
mod add_module_rate;
mod add_user_css;
mod fmt_alignments;
mod fmt_newline;

use crate::ftml_fmt::add_footnote_block::add_footnote_block;
use crate::ftml_fmt::add_module_rate::add_module_rate;
use crate::ftml_fmt::add_user_css::add_user_css;
use crate::ftml_fmt::{fmt_alignments::format_alignments, fmt_newline::format_newline};
use std::fs;

// These are temp directory paths.
pub(crate) const OUTPUT_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/output.ftml");

// This const is public for `src-tauri` to use.
pub const USER_CSS_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/user_css.css");

/// This function formats the ftml string.
pub fn ftml_fmt(ftml: &str) -> String {
    // read output from interpreter's temp output file
    let read_ftml = fs::read_to_string(OUTPUT_PATH);
    let ftml = read_ftml.as_deref().unwrap_or(ftml);

    // format the ftml string
    // normalize wikitext pipeline is here
    let output = format_newline(ftml);
    let output = format_alignments(&output);

    // add module rate; on a missing/unreadable status file, leave content untouched
    let output = add_module_rate(&output).unwrap_or(output);

    // attach user css
    let user_css = fs::read_to_string(USER_CSS_PATH);
    let output = add_user_css(&output, user_css.as_deref().ok());

    // add footnote block
    let output = add_footnote_block(&output);

    // write output to interpreter's temp output file back
    if read_ftml.is_ok() {
        let _ = fs::write(OUTPUT_PATH, &output);
    }

    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ftml_fmt() {
        let origin = "a\n\n\n\n\n\nb"; // <- This is a placeholder
        let output = ftml_fmt(origin);

        println!("{output}");
    }
}
