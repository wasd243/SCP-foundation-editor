use regex::Regex;

use super::model::{TabItem, TabViewData};

pub fn parse_tabview_data(source: &str) -> Option<TabViewData> {
    let caps = Regex::new(r#"(?is)^\[\[tabview\]\](.*?)\[\[/tabview\]\]$"#)
        .unwrap()
        .captures(source)?;
    let content = caps.get(1)?.as_str();
    let tab_re = Regex::new(r#"(?is)\[\[tab\s+([^\]]+)\]\](.*?)\[\[/tab\]\]"#).unwrap();

    let tabs = tab_re
        .captures_iter(content)
        .filter_map(|caps| {
            Some(TabItem {
                title: caps.get(1)?.as_str().to_string(),
                body: caps.get(2)?.as_str().to_string(),
            })
        })
        .collect::<Vec<_>>();

    Some(TabViewData {
        // source: source.to_string(),
        tabs,
    })
}
