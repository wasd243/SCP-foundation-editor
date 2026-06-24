use regex::Regex;

/// Removes only the last `@@@@` (forced newline) token from the ftml string.
/// Earlier `@@@@` tokens are left untouched; if none exist the input is returned as-is.
pub(super) fn remove_trailing_break_force_newline(ftml: &str) -> String {
    let re_ignore_when_no_footnote = Regex::new(r"(?is)\[\[footnote]].*?\[\[/footnote]]").unwrap();

    if !re_ignore_when_no_footnote.is_match(ftml) {
        return ftml.to_string();
    }

    match ftml.rfind("@@@@") {
        Some(index) => {
            let mut output = String::with_capacity(ftml.len());
            output.push_str(&ftml[..index]);
            output.push_str(&ftml[index + "@@@@".len()..]);
            output
        }
        None => ftml.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_remove_trailing_break_force_newline() {
        assert_eq!(
            remove_trailing_break_force_newline("a\n\n\n\n\nb"),
            "a\n\n\n\n\nb"
        );

        assert_eq!(
            remove_trailing_break_force_newline("a\n@@@@\n@@@@\nb"),
            "a\n@@@@\n@@@@\nb"
        );

        assert_eq!(
            remove_trailing_break_force_newline(
                "a[[footnote]]a[[/footnote]]\n@@@@\n@@@@\n@@@@\nb\n@@@@"
            ),
            "a[[footnote]]a[[/footnote]]\n@@@@\n@@@@\n@@@@\nb\n"
        );
    }
}
