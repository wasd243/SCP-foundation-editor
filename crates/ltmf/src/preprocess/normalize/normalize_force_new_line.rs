use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

pub(super) fn normalize_force_new_line_to_paragraph(value: Value) -> Value {
    rename_type(value, "ForceNewLine", "paragraph")
}
