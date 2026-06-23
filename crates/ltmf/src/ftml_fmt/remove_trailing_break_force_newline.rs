/// Removes only the last `@@@@` (forced newline) token from the ftml string.
/// Earlier `@@@@` tokens are left untouched; if none exist the input is returned as-is.
pub(super) fn remove_trailing_break_force_newline(ftml: &str) -> String {
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
    fn removes_the_only_token() {
        assert_eq!(remove_trailing_break_force_newline("a@@@@b"), "ab");
    }

    #[test]
    fn removes_only_the_last_token() {
        assert_eq!(remove_trailing_break_force_newline("@@@@x@@@@y"), "@@@@xy");
    }

    #[test]
    fn leaves_string_without_token_unchanged() {
        assert_eq!(remove_trailing_break_force_newline("abc"), "abc");
    }

    #[test]
    fn removes_trailing_token() {
        assert_eq!(remove_trailing_break_force_newline("a\n@@@@"), "a\n");
    }
}
