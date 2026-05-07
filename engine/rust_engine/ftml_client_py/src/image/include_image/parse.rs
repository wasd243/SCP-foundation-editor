use regex::Regex;

use super::model::IncludeImageData;

pub fn normalize_center_wrapper(text: &str) -> String {
    let re = Regex::new(r#"(?is)\[\[=\]\]\s*(\[\[include component:image-block.*?\]\])\s*\[\[/=\]\]"#)
        .unwrap();

    re.replace_all(text, |caps: &regex::Captures| {
        let mut content = caps.get(1).map(|m| m.as_str()).unwrap_or_default().to_string();
        if Regex::new(r#"(?i)align=[^|\]\n]+"#).unwrap().is_match(&content) {
            Regex::new(r#"(?i)align=[^|\]\n]+"#)
                .unwrap()
                .replace_all(&content, "align=center")
                .to_string()
        } else {
            content = content.replace("]]", " |align=center]]");
            content
        }
    })
    .to_string()
}

fn get_arg(source: &str, name: &str) -> String {
    let pattern = format!(r#"(?i)(?:\||\s+)\s*{}\s*=\s*([^\|\n\]]+)"#, regex::escape(name));
    Regex::new(&pattern)
        .unwrap()
        .captures(source)
        .and_then(|caps| caps.get(1))
        .map(|m| m.as_str().trim().to_string())
        .unwrap_or_default()
}

pub fn parse_include_image(source: &str) -> IncludeImageData {
    IncludeImageData {
        name: get_arg(source, "name"),
        caption: get_arg(source, "caption"),
        width: get_arg(source, "width"),
        height: get_arg(source, "height"),
        align: get_arg(source, "align"),
    }
}
