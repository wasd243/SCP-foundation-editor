#![allow(non_snake_case)]

use regex::Regex;

#[derive(Debug, Clone)]
pub struct AimData {
    pub blocks_arg: String,
    pub row_style_top: &'static str,
    pub row_style_bottom: &'static str,
    pub XXXX: String,
    pub lv: String,
    pub cc: String,
    pub dc: String,
    pub site: String,
    pub dir: String,
    pub head: String,
    pub mtf: String,
}

pub fn parse_aim_data(source: &str) -> AimData {
    let blocks_arg = get_arg(source, "blocks");
    let row_style_top = if blocks_arg == "!" {
        "display:none;"
    } else {
        ""
    };
    let row_style_bottom = if blocks_arg == "-" {
        "display:none;"
    } else {
        ""
    };

    AimData {
        blocks_arg,
        row_style_top,
        row_style_bottom,
        XXXX: get_arg(source, "XXXX"),
        lv: get_arg(source, "lv"),
        cc: get_arg(source, "cc"),
        dc: get_arg(source, "dc"),
        site: get_arg(source, "site"),
        dir: get_arg(source, "dir"),
        head: get_arg(source, "head"),
        mtf: get_arg(source, "mtf"),
    }
}

fn get_arg(source: &str, name: &str) -> String {
    let pattern = format!(
        r"(?i)(?:\||\s+)\s*{}\s*=\s*([^\|\n\]]+)",
        regex::escape(name)
    );
    Regex::new(&pattern)
        .unwrap()
        .captures(source)
        .and_then(|captures| captures.get(1))
        .map(|value| value.as_str().trim().to_string())
        .unwrap_or_else(|| "???".to_string())
}
