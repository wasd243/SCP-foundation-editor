mod add_module_rate;
mod add_user_css;
mod fmt_alignments;
mod fmt_newline;
mod remove_trailing_break_force_newline;

use crate::ftml_fmt::add_module_rate::add_module_rate;
use crate::ftml_fmt::add_user_css::{add_user_css, remove_unused_module_css};
use crate::ftml_fmt::remove_trailing_break_force_newline::remove_trailing_break_force_newline;
use crate::ftml_fmt::{fmt_alignments::format_alignments, fmt_newline::format_newline};
use crate::paths::temp_dir;
use std::fs;
use std::path::PathBuf;

// These are temp directory paths.
pub(crate) fn output_path() -> PathBuf {
    temp_dir().join("output.ftml")
}

// This path is public for `src-tauri` to use.
pub fn user_css_path() -> PathBuf {
    temp_dir().join("user_css.css")
}

/// This function formats the ftml string.
pub fn ftml_fmt(ftml: &str) -> String {
    // read output from interpreter's temp output file
    let read_ftml = fs::read_to_string(output_path());
    let ftml = read_ftml.as_deref().unwrap_or(ftml);

    // format the ftml string
    // normalize wikitext pipeline is here
    let output = format_newline(ftml);
    let output = format_alignments(&output);

    // add module rate; on a missing/unreadable status file, leave content untouched
    let output = add_module_rate(&output).unwrap_or(output);

    // attach user css
    let user_css = fs::read_to_string(user_css_path());
    let output = add_user_css(&output, user_css.as_deref().ok());

    // strip the placeholder module when no user css was provided
    // and then remove trailing break force newline
    let output = remove_unused_module_css(&output);
    let output = remove_trailing_break_force_newline(&output);

    // write output to interpreter's temp output file back
    if read_ftml.is_ok() {
        let _ = fs::write(output_path(), &output);
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
