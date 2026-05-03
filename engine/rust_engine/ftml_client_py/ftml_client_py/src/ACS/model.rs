#[derive(Debug, Clone)]
pub struct AcsData {
    pub item: String,
    pub clr: String,
    pub cnt: String,
    pub sec: String,
    pub sec_icon: String,
    pub dsr: String,
    pub rsk: String,
    pub is_shiver: bool,
}

pub fn color_for(cnt: &str) -> &'static str {
    match cnt {
        "safe" => "#27ae60",
        "euclid" => "#f1c40f",
        "keter" => "#c0392b",
        "neutralized" => "#7f8c8d",
        "pending" => "#bdc3c7",
        "explained" => "#95a5a6",
        "esoteric" | "\u{673a}\u{5bc6}" => "#595959",
        _ => "#595959",
    }
}

pub fn icon_for(sec: &str) -> Option<&'static str> {
    match sec {
        "apollyon" => Some(
            "https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/apollyon-icon.svg",
        ),
        "archon" => Some(
            "https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/archon-icon.svg",
        ),
        "hiemal" => Some(
            "https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/hiemal-icon.svg",
        ),
        "tiamat" => Some(
            "https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/tiamat-icon.svg",
        ),
        "ticonderoga" => Some(
            "https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/ticonderoga-icon.svg",
        ),
        "thaumiel" => Some(
            "https://scp-wiki.wdfiles.com/local--files/component%3Aanomaly-class-bar/thaumiel-icon.svg",
        ),
        _ => None,
    }
}
