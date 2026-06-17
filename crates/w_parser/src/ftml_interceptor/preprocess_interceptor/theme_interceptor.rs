use regex::Regex;

pub fn theme_interceptor(ftml: &str) -> String {
    // This regex matches any `[[include :theme:...]]`
    let re = Regex::new(r"\s*\[\[include\s+:[^\]]*?:theme:[^\]]*?\]\]").unwrap();
    re.replace_all(ftml, "").to_string()
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
}
