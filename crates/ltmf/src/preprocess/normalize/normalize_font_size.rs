use serde_json::{value, Value};
use crate::preprocess::normalize::rename::rename_type;

pub fn normalize_font_size(value: Value) -> Value {
    rename_type(value, "fontSize", "Size")
}
