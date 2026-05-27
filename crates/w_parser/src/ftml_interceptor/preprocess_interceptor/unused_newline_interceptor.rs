use regex::Regex;

pub fn unused_newline_interceptor(wikitext: &str) -> String {
    let re_remove_unused_newline =
        Regex::new(r#"(?i)(style="width:[^"\r\n]+)\s*[\r\n]+\s*(")"#).unwrap();

    re_remove_unused_newline
        .replace_all(wikitext, "$1$2")
        .into_owned()
}
