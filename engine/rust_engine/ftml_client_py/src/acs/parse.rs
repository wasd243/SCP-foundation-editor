use regex::Regex;

use super::model::{AcsData, icon_for};

pub fn inject_shivering(text: &str) -> String {
    let re = Regex::new(
        r#"(?s)\[\[div class="Shivering-acs"\]\]\s*\[\[include :scp-wiki-cn:component:anomaly-class-bar-source(.*?)\]\]\s*\[\[/div\]\]"#,
    )
    .unwrap();

    re.replace_all(
        text,
        r"[[include :scp-wiki-cn:component:anomaly-class-bar-source$1 |data-shivering=true]]",
    )
    .to_string()
}

pub fn extract_acs_data(source: &str) -> AcsData {
    let item = get_arg(source, "item-number");
    let clearance = get_arg(source, "clearance");
    let clr = Regex::new(r"\d+")
        .unwrap()
        .find(&clearance)
        .map(|mat| mat.as_str().to_string())
        .unwrap_or_else(|| "1".to_string());
    let mut cnt = get_arg(source, "container-class").to_lowercase();
    let sec = get_arg(source, "secondary-class").to_lowercase();
    let mut sec_icon = get_arg(source, "secondary-icon");
    let dsr = get_arg(source, "disruption-class");
    let rsk = get_arg(source, "risk-class");

    if !sec.is_empty() && sec != "none" {
        cnt = "\u{673a}\u{5bc6}".to_string();
        if sec_icon.is_empty()
            && let Some(icon) = icon_for(&sec)
        {
            sec_icon = icon.to_string();
        }
    }

    AcsData {
        item,
        clr,
        cnt,
        sec,
        sec_icon,
        dsr,
        rsk,
        is_shiver: get_arg(source, "data-shivering") == "true",
    }
}

fn get_arg(source: &str, name: &str) -> String {
    let pattern = format!(r"(?:\||\s){}=([^\|\n\]]+)", regex::escape(name));
    Regex::new(&pattern)
        .unwrap()
        .captures(source)
        .and_then(|captures| captures.get(1))
        .map(|value| value.as_str().trim().to_string())
        .unwrap_or_default()
}
