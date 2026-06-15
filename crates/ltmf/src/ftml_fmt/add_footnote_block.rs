/// This function adds a footnote block to the ftml string.
/// This exists for formated wikitext of `[[footnoteblock]]` support.
/// Although the footnote block cannot be moved by user in the editor.
pub(super) fn add_footnote_block(ftml: &str) -> String {
    let output = format!("{ftml}\n\n[[footnoteblock]]");
    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_footnote_block() {
        let ftml = "content";
        let output = add_footnote_block(ftml);
        assert_eq!(output, "content\n\n[[footnoteblock]]");
    }
}
