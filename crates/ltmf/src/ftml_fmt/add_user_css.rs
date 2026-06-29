use regex::Regex;

pub(super) fn add_user_css(ftml: &str, user_css: Option<&str>) -> String {
    match user_css {
        Some(user_css) => format!("[[module css]]{user_css}[[/module]]\n\n{ftml}"),
        None => ftml.to_string(),
    }
}

/// Well, I couldn't find where the `/* NO USER CSS */` is.
/// It seems like to be a fallback in the frontend, so I add this patch function to clean the code format.
pub(super) fn remove_unused_module_css(ftml: &str) -> String {
    let re = Regex::new(r"(?i)\[\[module css]]\n/\* NO USER CSS \*/\n\[\[/module]]").unwrap();
    if re.is_match(ftml) {
        re.replace_all(ftml, "").to_string()
    } else {
        ftml.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_user_css_to_head() {
        let output = add_user_css("content", Some(".test { color: red; }"));

        assert_eq!(
            output,
            "[[module css]].test { color: red; }[[/module]]\n\ncontent"
        );
    }

    #[test]
    fn keeps_ftml_when_user_css_is_missing() {
        assert_eq!(add_user_css("content", None), "content");
    }

    #[test]
    fn test_remove_unused_module_css() {
        assert_eq!(
            remove_unused_module_css("[[module css]]\n/* NO USER CSS */\n[[/module]]\n\ncontent"),
            "\n\ncontent"
        );
    }
}
