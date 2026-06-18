use regex::Regex;

/// This function formats the left alignments.
fn format_left_alignments(ftml: &str) -> String {
    let re = Regex::new(r#"(?s)\[\[<]](.*?)\n\[\[/<]]\n\n\[\[<]](.*?)\n\[\[/<]]"#).unwrap();
    let mut output = ftml.to_string();
    loop {
        let next = re.replace_all(&output, "[[<]]$1\n$2\n[[/<]]").to_string();
        if next == output {
            break;
        }
        output = next;
    }
    output
}

/// This function formats the right alignments.
fn format_right_alignments(ftml: &str) -> String {
    let re = Regex::new(r#"(?s)\[\[>]](.*?)\n\[\[/>]]\n\n\[\[>]](.*?)\n\[\[/>]]"#).unwrap();
    let mut output = ftml.to_string();
    // A loop is needed because the regex will match the same string multiple times.
    loop {
        let next = re.replace_all(&output, "[[>]]$1\n$2\n[[/>]]").to_string();
        if next == output {
            break;
        }
        output = next;
    }
    output
}

/// This function formats the center alignments.
fn format_center_alignments(ftml: &str) -> String {
    let re = Regex::new(r#"(?s)\[\[=]](.*?)\n\[\[/=]]\n\n\[\[=]](.*?)\n\[\[/=]]"#).unwrap();
    let mut output = ftml.to_string();
    loop {
        let next = re.replace_all(&output, "[[=]]$1\n$2\n[[/=]]").to_string();
        if next == output {
            break;
        }
        output = next;
    }
    output
}

/// This function is public super `ftml_fmt.rs` to use.
/// This format_alignments does not include in `@@@@`, I don't know why, but it's unnecessary to add `@@@@` into regex.
/// Because it also works on ftml, not planned to fix.
pub(super) fn format_alignments(ftml: &str) -> String {
    let output = format_left_alignments(ftml);
    let output = format_right_alignments(&output);

    format_center_alignments(&output)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_left_alignments() {
        let ftml = "[[<]]\ntest1\n[[/<]]\n\n[[<]]\ntest2\n[[/<]]\n\n[[<]]\ntest3\n[[/<]]\n[[module rate]]\n\ntest4";
        let output = format_left_alignments(ftml);
        assert_eq!(
            output,
            "[[<]]\ntest1\n\ntest2\n\ntest3\n[[/<]]\n[[module rate]]\n\ntest4"
        );
    }

    #[test]
    fn test_format_right_alignments() {
        let ftml = "[[>]]\ntest1\n[[/>]]\n\n[[>]]\ntest2\n[[/>]]\n\n[[>]]\ntest3\n[[/>]]\n[[module rate]]\n\ntest4";
        let output = format_right_alignments(ftml);
        assert_eq!(
            output,
            "[[>]]\ntest1\n\ntest2\n\ntest3\n[[/>]]\n[[module rate]]\n\ntest4"
        );
    }

    #[test]
    fn test_format_center_alignments() {
        let ftml = "[[=]]\ntest1\n[[/=]]\n\n[[=]]\ntest2\n[[/=]]\n\n[[=]]\ntest3\n[[/=]]\n[[module rate]]\n\ntest4";
        let output = format_center_alignments(ftml);
        assert_eq!(
            output,
            "[[=]]\ntest1\n\ntest2\n\ntest3\n[[/=]]\n[[module rate]]\n\ntest4"
        );
    }
}
