#[derive(Debug, Clone)]
pub struct LicenseFileData {
    pub file_name: String,
    pub img_name: String,
    pub img_author: String,
    pub img_license: String,
    pub source_link: String,
    pub derived_from: String,
    pub note: String,
}

#[derive(Debug, Clone)]
pub struct LicenseData {
    // TODO: future undo support, or debugging
    // pub source: String,
    pub author: String,
    pub translator: String,
    pub is_original: bool,
    pub files: Vec<LicenseFileData>,
}
