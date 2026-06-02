use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

pub fn normalize_font_size(value: Value) -> Value {
    rename_type(value, "fontSize", "Size")
}
