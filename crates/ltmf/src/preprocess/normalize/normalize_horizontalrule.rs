// Only a upper case H
use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

pub(super) fn normalize_horizontalrule(value: Value) -> serde_json::Value {
    rename_type(value, "horizontalRule", "HorizontalRule")
}
