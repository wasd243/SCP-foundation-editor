#[derive(Debug, Clone)]
pub struct TabItem {
    pub title: String,
    pub body: String,
}

#[derive(Debug, Clone)]
pub struct TabViewData {
    // pub source: String,
    pub tabs: Vec<TabItem>,
}
