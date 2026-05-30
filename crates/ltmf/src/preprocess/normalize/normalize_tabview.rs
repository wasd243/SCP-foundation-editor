use serde_json::Value;
use crate::preprocess::normalize::rename::rename_type;

pub fn normalize_tabview(value: Value) -> Value {
    let value = rename_type(value, "tabViewButton", "tab");
    let value = rename_type(value, "tabViewButtonList", "TabViewButtonList");
    delete_tabview_attrs(value)
}

fn delete_tabview_attrs(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            let is_tabview_node = map
                .get("type")
                .and_then(Value::as_str)
                .is_some_and(is_tabview_node_type);

            if is_tabview_node {
                map.remove("attrs");
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, delete_tabview_attrs(value)))
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(delete_tabview_attrs)
                .collect(),
        ),
        _ => value,
    }
}

fn is_tabview_node_type(node_type: &str) -> bool {
    matches!(
        node_type,
        "tabView" | "tab" | "tabViewButtonList" | "tabViewPanelList" | "tabViewPanel"
    )
}
