use regex::Regex;

pub fn unused_variable_interceptor(wikitext: &str) -> String {
    let re_remove_unused_variable = Regex::new(r#"(?i)\s+link=\{\$link}"#).unwrap();

    re_remove_unused_variable.replace_all(wikitext, "").into_owned()
}
