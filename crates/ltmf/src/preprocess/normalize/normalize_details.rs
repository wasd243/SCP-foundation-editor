// This function renames and removes unused details attrs.
use crate::preprocess::normalize::rename::rename_type;
use serde_json::Value;

fn rename_details(value: Value) -> Value {
    let value = rename_type(value, "details", "Collapsible");
    let value = rename_type(value, "detailsSummary", "CollapsibleSummary");
    rename_type(value, "detailsContent", "CollapsibleContent")
}

pub fn normalize_details(value: Value) -> Value {
    let value = rename_details(value);
    remove_collapsible_attrs(value)
}

fn remove_collapsible_attrs(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let remove_attrs = should_remove_collapsible_attrs(&Value::Object(map.clone()));

            Value::Object(
                map.into_iter()
                    .filter_map(|(key, value)| {
                        if remove_attrs && key == "attrs" {
                            None
                        } else {
                            Some((key, remove_collapsible_attrs(value)))
                        }
                    })
                    .collect(),
            )
        }
        Value::Array(values) => {
            Value::Array(values.into_iter().map(remove_collapsible_attrs).collect())
        }
        _ => value,
    }
}

fn should_remove_collapsible_attrs(value: &Value) -> bool {
    value
        .get("type")
        .and_then(Value::as_str)
        .is_some_and(|node_type| {
            node_type == "Collapsible" && has_attrs_class(value, "wj-collapsible")
                || node_type == "CollapsibleSummary"
                    && has_attrs_class(value, "wj-collapsible-button wj-collapsible-button-top")
        })
}

fn has_attrs_class(value: &Value, class_name: &str) -> bool {
    value
        .get("attrs")
        .and_then(|attrs| attrs.get("class"))
        .and_then(Value::as_str)
        == Some(class_name)
}
