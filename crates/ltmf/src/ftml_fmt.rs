mod fmt_newline;

use crate::ftml_fmt::fmt_newline::format_newline;
use std::fs;

const OUTPUT_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/output.ftml");

/// This function formats the ftml string.
pub fn ftml_fmt(ftml: &str) -> String {
    // read output from interpreter's temp output file
    let read_ftml = fs::read_to_string(OUTPUT_PATH);
    let ftml = read_ftml.as_deref().unwrap_or(ftml);

    // format the ftml string
    let output = format_newline(ftml);

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
        let origin = "a\n\n\n\n\n\nb";
        let output = ftml_fmt(origin);
        assert_eq!(output, "a\n\nb");

        println!("{output}");
    }
}
