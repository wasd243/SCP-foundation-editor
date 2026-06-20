use regex::Regex;
use std::fs;

use crate::paths::temp_dir;

pub fn rate_interceptor(text: &str) -> String {
    let re = Regex::new(r"(?i)\[\[module rate\]\]").unwrap();

    let rate_temp_path = temp_dir().join("module_rate_status.txt");

    if re.is_match(text) {
        let alignment = detect_alignment(text);
        let content = format!("MODULE_RATE=TRUE\nALIGNMENTS={alignment}");
        fs::write(&rate_temp_path, content).unwrap();
    } else {
        fs::write(&rate_temp_path, "MODULE_RATE=FALSE\nALIGNMENTS=NONE").unwrap();
    }

    re.replace_all(text, "").to_string()
}

fn detect_alignment(text: &str) -> &'static str {
    let left = Regex::new(r"(?i)(?s)\[\[<\]\].*?\[\[module rate\]\].*?\[\[/<\]\]").unwrap();
    let right = Regex::new(r"(?i)(?s)\[\[>\]\].*?\[\[module rate\]\].*?\[\[/>\]\]").unwrap();
    let center = Regex::new(r"(?i)(?s)\[\[=\]\].*?\[\[module rate\]\].*?\[\[/=\]\]").unwrap();

    if left.is_match(text) {
        "LEFT"
    } else if right.is_match(text) {
        "RIGHT"
    } else if center.is_match(text) {
        "CENTER"
    } else {
        "NONE"
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_rate_interceptor_removes_tag() {
        let text = "[[module rate]]This is a test";
        let expected = "This is a test";
        assert_eq!(rate_interceptor(text), expected);
    }

    #[test]
    fn test_temp_file_is_created() {
        let text = "[[module rate]]This is a test";
        rate_interceptor(text);
        assert!(fs::metadata(temp_dir().join("module_rate_status.txt")).is_ok());
    }
}
