pub(super) fn add_user_css(ftml: &str, user_css: Option<&str>) -> String {
    match user_css {
        Some(user_css) => format!("[[module css]]{user_css}[[/module]]\n\n{ftml}"),
        None => ftml.to_string(),
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
}
