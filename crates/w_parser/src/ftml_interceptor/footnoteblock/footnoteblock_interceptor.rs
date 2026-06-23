use regex::Regex;

/// This function exists because the ftml parser will `STATUS_STACK_OVERFLOW`
/// When parsing
///
/// ```wikitext
/// [[footnote]][[footnoteblock]][[/footnote]]
/// ```
///
/// ---
///
/// So we need to intercept it before ftml parsing it.
/// This is a patch function, will be removed after the ftml parser team fixes it.
pub fn intercept_footnote_block(text: &str) -> String {
    let re_ignore = Regex::new(r"(?i)@@\[\[footnoteblock]]@@").unwrap();
    if re_ignore.is_match(text) {
        return text.to_string();
    }

    let re = Regex::new(r"(?i)\[\[footnoteblock]]").unwrap();
    re.replace_all(text, "").to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_intercept_footnote_block() {
        let text = "[[footnote]][[footnoteblock]][[/footnote]]";
        assert_eq!(intercept_footnote_block(text), "[[footnote]][[/footnote]]");
    }

    #[test]
    fn test_intercept_footnote_block_ignore() {
        let text = "line1\n@@[[footnoteblock]]@@\nline3";
        assert_eq!(intercept_footnote_block(text), text);
    }
}
