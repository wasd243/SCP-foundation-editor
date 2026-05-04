use regex::Regex;

use super::model::FootnoteData;

pub fn parse_standard_footnote(source: &str) -> Option<FootnoteData> {
    let caps = Regex::new(r#"(?is)^\[\[footnote\]\](.*?)\[\[/footnote\]\]$"#)
        .unwrap()
        .captures(source)?;

    Some(FootnoteData {
        source: source.to_string(),
        content: caps.get(1)?.as_str().to_string(),
    })
}

pub fn parse_better_footnote(source: &str) -> Option<FootnoteData> {
    let caps = Regex::new(
        r#"(?is)^\[\[span\s+class=["']fnnum["']\]\](.*?)\[\[/span\]\]\[\[span\s+class=["']fncon["']\]\](.*?)\[\[/span\]\]$"#,
    )
    .unwrap()
    .captures(source)?;

    Some(FootnoteData {
        source: source.to_string(),
        content: caps.get(2)?.as_str().to_string(),
    })
}
