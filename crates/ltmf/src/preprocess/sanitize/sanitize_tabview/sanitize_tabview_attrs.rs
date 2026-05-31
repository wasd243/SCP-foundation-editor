use serde_json::Value;

// sanitize tabview unused attrs like
//   "attrs": {
//     "class": "wj-tabs-button-list",
//     "role": "tablist"
//   }

fn is_tabview_button_list_attrs(value: &Value) -> bool {
    value.as_object().is_some_and(|attrs| {
        attrs.len() == 2
            && attrs.get("class").and_then(Value::as_str) == Some("wj-tabs-button-list")
            && attrs.get("role").and_then(Value::as_str) == Some("tablist")
    })
}

pub fn sanitize_tabview_attrs(json: &Value) -> Value {
    match json {
        Value::Object(map) => Value::Object(
            map.iter()
                .filter_map(|(key, value)| {
                    if key == "attrs" && is_tabview_button_list_attrs(value) {
                        None
                    } else {
                        Some((key.clone(), sanitize_tabview_attrs(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.iter().map(sanitize_tabview_attrs).collect()),
        _ => json.clone(),
    }
}
