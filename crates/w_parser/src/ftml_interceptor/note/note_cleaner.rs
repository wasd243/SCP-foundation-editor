use regex::Regex;

pub fn note_cleaner(note_text: &str) -> String {
    // Trim leading/trailing <br> tags around note content
    let leading_br_re = Regex::new(r"(?is)^\s*(?:<br\b[^>]*>\s*)+").unwrap();
    let trailing_br_re = Regex::new(r"(?is)(?:\s*<br\b[^>]*>)+\s*$").unwrap();

    // Fix malformed wrappers generated like:
    // <p><div class="wj-note"></p> ... <p></div></p>
    let malformed_open_div_re =
        Regex::new(r#"(?is)<p>\s*(<div\b[^>]*class\s*=\s*["']wj-note["'][^>]*>)\s*</p>"#).unwrap();
    let malformed_close_div_re = Regex::new(r"(?is)<p>\s*</div>\s*</p>").unwrap();

    let note_text = malformed_open_div_re.replace(note_text, "$1");
    let note_text = malformed_close_div_re.replace(&note_text, "</div>");
    let note_text = leading_br_re.replace(&note_text, "");

    trailing_br_re.replace(&note_text, "").to_string()
}
