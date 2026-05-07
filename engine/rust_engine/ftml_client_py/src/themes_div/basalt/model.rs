#[derive(Debug, Clone)]
pub struct BasaltDivData {
    pub classes: Vec<String>,
    pub source_div: String,
    pub inner_content: String,
    pub end_pos: usize,
}

#[derive(Debug, Clone)]
pub enum BasaltDivKind {
    Floatbox { right: bool },
    Special {
        primary_class: String,
        box_class: &'static str,
    },
}

pub const BASALT_SPECIAL_MAP: &[(&str, &str)] = &[
    ("blockquote", "basalt-blockquote-box"),
    ("notation", "basalt-notation-box"),
    ("jotting", "basalt-jotting-box"),
    ("modal", "basalt-modal-box"),
    ("smallmodal", "basalt-smallmodal-box"),
    ("papernote", "basalt-papernote-box"),
    ("document", "basalt-document-box"),
    ("darkdocument", "basalt-darkdocument-box"),
    ("raisa_memo", "basalt-raisa_memo-box"),
    ("classification_memo", "basalt-classification_memo-box"),
    ("ettra_memo", "basalt-ettra_memo-box"),
    ("ethics_memo", "basalt-ethics_memo-box"),
    ("temporal_memo", "basalt-temporal_memo-box"),
    ("overwatch_memo", "basalt-overwatch_memo-box"),
    ("miscomm_memo", "basalt-miscomm_memo-box"),
];
