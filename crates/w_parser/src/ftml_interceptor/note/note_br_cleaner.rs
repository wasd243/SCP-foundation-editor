use regex::Regex;

pub fn clean_note_br(note_text: &str) -> String {
    let leading_br_re = Regex::new(r"(?is)^\s*(?:<br\b[^>]*>\s*)+").unwrap();
    let trailing_br_re = Regex::new(r"(?is)(?:\s*<br\b[^>]*>)+\s*$").unwrap();

    let note_text = leading_br_re.replace(note_text, "");
    trailing_br_re.replace(&note_text, "").to_string()
}
