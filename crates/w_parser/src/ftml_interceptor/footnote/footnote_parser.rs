use regex::Regex;

pub fn footnote_parser(text: &str) -> String {
    // Identify content inside ~_FOOTNOTE_~
    let footnote_re = Regex::new(r"(?is)~_FOOTNOTE_BEGIN_~(.*?)~_FOOTNOTE_END_~").unwrap();

    if !footnote_re.is_match(text) {
        return text.into();
    }

    footnote_re
        .replace_all(text, |captures: &regex::Captures| {
            let content = captures.get(1).map_or("", |matched| matched.as_str());
            format!("<footnote>{content}</footnote>")
        })
        .into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_footnote_parser() {
        let text = "~_FOOTNOTE_BEGIN_~This is a footnote~_FOOTNOTE_END_~";
        let expected = "<footnote>This is a footnote</footnote>";
        assert_eq!(footnote_parser(text), expected);
    }

    #[test]
    fn test_footnote_parser_multiple() {
        let text =
            "a ~_FOOTNOTE_BEGIN_~one~_FOOTNOTE_END_~ b ~_FOOTNOTE_BEGIN_~two~_FOOTNOTE_END_~";
        let expected = "a <footnote>one</footnote> b <footnote>two</footnote>";
        assert_eq!(footnote_parser(text), expected);
    }

    #[test]
    fn test_footnote_parser_no_placeholder() {
        let text = "<p>nothing to do</p>";
        assert_eq!(footnote_parser(text), text);
    }
}
