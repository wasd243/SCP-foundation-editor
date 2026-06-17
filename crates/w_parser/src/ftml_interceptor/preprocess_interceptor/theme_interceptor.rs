use regex::Regex;
use serde::{Deserialize, Serialize};
use std::fs;

/// This constant is public for the whole project to use.
pub const THEME_STATUS_TEMP_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/theme_status.json");

#[derive(Serialize, Deserialize, Debug)]
pub struct ThemeStatus {
    pub theme: bool,
    pub theme_name: Option<String>,
    pub parent_theme: Option<bool>,
    pub parent_theme_name: Vec<String>,
}

pub fn theme_interceptor(ftml: &str) -> String {
    // This regex matches any `[[include :theme:...]]`
    let re = Regex::new(r"\s*\[\[include\s+:[^\]]*?:theme:[^\]]*?\]\]").unwrap();

    // Add adapter here:
    write_theme_boolean_status(re.is_match(ftml));

    re.replace_all(ftml, "").to_string()
}

/// Writes the theme boolean status to the temp file. When a theme include is matched,
/// `theme` is `true`; otherwise `false`. All other fields are left as
/// `null` / `[]` placeholders for later population.
///
/// ---
///
/// Tip: Only write `theme` boolean and full all others `null` or `[]`.
fn write_theme_boolean_status(matched: bool) {
    let status = ThemeStatus {
        theme: matched,
        theme_name: None,
        parent_theme: None,
        parent_theme_name: Vec::new(),
    };

    if let Ok(contents) = serde_json::to_string_pretty(&status) {
        let _ = fs::write(THEME_STATUS_TEMP_PATH, contents);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_theme_interceptor() {
        let ftml = r#"[[include :scp-wiki:theme:test]]"#;
        assert_eq!(theme_interceptor(ftml), "");
    }

    #[test]
    fn test_wired_theme_name_with_include_variables() {
        let ftml = r#"
        [[include :scp-wiki:theme:test
        |var1=value1
        |var2=value2]]"#;
        assert_eq!(theme_interceptor(ftml), "");
    }

    #[test]
    fn test_wired_theme_name_with_include_variables_without_newline() {
        let ftml = r#"[[include :scp-wiki:theme:test|var1=value1|var2=value2]]"#;
        assert_eq!(theme_interceptor(ftml), "");
    }

    #[test]
    fn test_normal_text() {
        let ftml = r#"This is a normal text."#;
        assert_eq!(theme_interceptor(ftml), ftml);
    }
}
