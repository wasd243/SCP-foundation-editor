use regex::Regex;

pub fn note_interceptor(text: &str) -> String {
    let open_re = Regex::new(r"(?i)\[\[note\]\]").unwrap();
    let close_re = Regex::new(r"(?i)\[\[/note\]\]").unwrap();

    let text = open_re.replace_all(text, "\n~_WJ_NOTE_EXTERNAL_PARSER_BEGIN_~\n");
    let text = close_re.replace_all(&text, "\n~_WJ_NOTE_EXTERNAL_PARSER_END_~\n");

    text.into_owned()
}
