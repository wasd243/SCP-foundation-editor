#[derive(Debug, Clone)]
pub struct TocPlaceholderData {
    pub source: String,
}

#[derive(Debug, Clone)]
pub struct TocHeadingData {
    pub source: String,
    pub prefix: String,
    pub pluses: String,
    pub anchor: String,
    pub title: String,
}
