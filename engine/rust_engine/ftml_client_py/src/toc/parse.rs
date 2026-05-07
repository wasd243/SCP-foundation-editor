use super::model::{TocHeadingData, TocPlaceholderData};

pub fn parse_toc_placeholder(source: &str) -> TocPlaceholderData {
    TocPlaceholderData {
        source: source.to_string(),
    }
}

pub fn parse_toc_heading(
    source: &str,
    prefix: &str,
    pluses: &str,
    anchor: &str,
    title: &str,
) -> TocHeadingData {
    TocHeadingData {
        source: source.to_string(),
        prefix: prefix.to_string(),
        pluses: pluses.to_string(),
        anchor: anchor.trim().to_string(),
        title: title.trim().to_string(),
    }
}
