use regex::Regex;
use crate::ftml_interceptor::note::note_br_cleaner::clean_note_br;

pub fn note_parser(text: &str) -> String {
    // Identify content inside <wj-note> tags
    let note_re = Regex::new(r"(?is)~_WJ_NOTE_EXTERNAL_PARSER_BEGIN_~(.*?)~_WJ_NOTE_EXTERNAL_PARSER_END_~").unwrap();

    if !note_re.is_match(text) {
        return text.into();
    }

    note_re
        .replace_all(text, |captures: &regex::Captures| {
            let content = captures.get(1).map_or("", |matched| matched.as_str());
            let content = clean_note_br(content);
            format!("<div class=\"wj-note\">{content}</div>")
        })
        .into_owned()
}
