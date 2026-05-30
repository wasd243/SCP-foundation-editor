use serde_json::Value;
use crate::preprocess::normalize::rename::rename_type;

pub fn normalize_tabview(value: Value) -> Value {
    rename_type(value, "tabViewButton", "tab")
}
