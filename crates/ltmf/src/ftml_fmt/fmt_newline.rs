use std::fs;

const OUTPUT_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/cache/output.ftml");

pub(super) fn format_newline(ftml: &str) -> String {
    let read_ftml = fs::read_to_string(OUTPUT_PATH);
    let ftml = read_ftml.as_deref().unwrap_or(ftml);
    let output = collapse_newlines(ftml);

    if read_ftml.is_ok() {
        let _ = fs::write(OUTPUT_PATH, &output);
    }

    output
}

/// This function collapses multiple newlines into two.
fn collapse_newlines(ftml: &str) -> String {
    let mut output = String::with_capacity(ftml.len());
    let mut newline_count = 0;

    for character in ftml.chars() {
        if character == '\n' {
            if newline_count < 2 {
                output.push(character);
            }

            newline_count += 1;
            continue;
        }

        newline_count = 0;
        output.push(character);
    }

    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn keeps_single_newline() {
        assert_eq!(collapse_newlines("a\nb"), "a\nb");
    }

    #[test]
    fn keeps_two_newlines() {
        assert_eq!(collapse_newlines("a\n\nb"), "a\n\nb");
    }

    #[test]
    fn collapses_three_newlines_to_two() {
        assert_eq!(collapse_newlines("a\n\n\nb"), "a\n\nb");
    }

    #[test]
    fn collapses_long_newline_runs_to_two() {
        assert_eq!(collapse_newlines("a\n\n\n\nb\n\n\nc"), "a\n\nb\n\nc");
    }
}
