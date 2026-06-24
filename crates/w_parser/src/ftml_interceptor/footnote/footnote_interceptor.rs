use regex::Regex;

pub fn footnote_interceptor(ftml: &str) -> String {
    let re = Regex::new(r"(?is)\[\[footnote]](.*?)\[\[/footnote]]").unwrap();
    re.replace_all(ftml, "~_FOOTNOTE_BEGIN_~${1}~_FOOTNOTE_END_~")
        .to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_footnote_interceptor() {
        let ftml = "[[footnote]]This is a footnote[[/footnote]]";
        let expected = "~_FOOTNOTE_BEGIN_~This is a footnote~_FOOTNOTE_END_~";
        assert_eq!(footnote_interceptor(ftml), expected);
    }
}
