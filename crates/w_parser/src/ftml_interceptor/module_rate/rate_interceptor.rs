use regex::Regex;

pub fn rate_interceptor(text: &str) -> String {
    let re = Regex::new(r"(?i)\[\[module rate\]\]").unwrap();

    re.replace_all(text, "").to_string()
}
