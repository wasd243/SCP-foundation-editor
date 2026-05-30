// This function renames and removes unused details attrs.
use serde_json::Value;
use crate::preprocess::normalize::rename::rename_type;

fn rename_details(value: Value) -> Value {
    let value = rename_type(value, "details", "Collapsible");
    let value = rename_type(value, "detailsSummary", "CollapsibleSummary");
    rename_type(value, "detailsContent", "CollapsibleContent")
}

pub fn normalize_details(value: Value) -> Value {
    rename_details(value)
}
