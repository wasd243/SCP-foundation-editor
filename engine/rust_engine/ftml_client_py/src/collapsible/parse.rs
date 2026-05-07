use regex::Regex;

use super::model::CollapsibleData;

pub fn parse_collapsible_data(source: &str) -> Option<CollapsibleData> {
    let caps = Regex::new(r#"(?is)^\[\[collapsible([^\]]*)\]\](.*?)\[\[/collapsible\]\]$"#)
        .unwrap()
        .captures(source)?;
    let params_str = caps.get(1).map(|m| m.as_str()).unwrap_or("").trim();
    let content = caps.get(2)?.as_str().to_string();

    let show_text = Regex::new(r#"show\s*=\s*"([^"]*)""#)
        .unwrap()
        .captures(params_str)
        .and_then(|caps| caps.get(1))
        .map(|m| m.as_str().to_string())
        .unwrap_or_else(|| "+ 展开".to_string());
    let hide_text = Regex::new(r#"hide\s*=\s*"([^"]*)""#)
        .unwrap()
        .captures(params_str)
        .and_then(|caps| caps.get(1))
        .map(|m| m.as_str().to_string())
        .unwrap_or_else(|| "- 收起".to_string());

    Some(CollapsibleData {
        source: source.to_string(),
        show_text,
        hide_text,
        content,
    })
}
