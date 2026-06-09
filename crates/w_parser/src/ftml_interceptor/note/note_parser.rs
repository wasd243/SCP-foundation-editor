use regex::Regex;

pub fn note_parser(text: &str) -> String {
    // Identify content inside ~_WJ_NOTE_EXTERNAL_PARSER_~
    let note_re =
        Regex::new(r"(?is)~_WJ_NOTE_EXTERNAL_PARSER_BEGIN_~(.*?)~_WJ_NOTE_EXTERNAL_PARSER_END_~")
            .unwrap();

    if !note_re.is_match(text) {
        return text.into();
    }

    note_re
        .replace_all(text, |captures: &regex::Captures| {
            let content = captures.get(1).map_or("", |matched| matched.as_str());
            format!("<div class=\"wj-note\">{content}</div>")
        })
        .into_owned()
}
