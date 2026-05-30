use serde_json::Value;

// Only sanitize aria-controls in tabview, not in details or accordion.
fn sanitize_aria_controls_in_tabview(value: Value, in_tabview: bool) -> Value {
    match value {
        Value::Object(map) => {
            let is_tabview = map
                .get("attrs")
                .and_then(|attrs| attrs.get("class"))
                .and_then(Value::as_str)
                .is_some_and(|class| class.split_whitespace().any(|class| class == "wj-tabs"));
            let in_tabview = in_tabview || is_tabview;

            Value::Object(
                map.into_iter()
                    .filter_map(|(key, value)| {
                        if in_tabview && key == "aria-controls" {
                            None
                        } else {
                            Some((key, sanitize_aria_controls_in_tabview(value, in_tabview)))
                        }
                    })
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(|value| sanitize_aria_controls_in_tabview(value, in_tabview))
                .collect(),
        ),
        _ => value,
    }
}

fn sanitize_aria_selected(value: Value) -> Value {
    match value {
        Value::Object(map) => Value::Object(
            map.into_iter()
                .filter_map(|(key, value)| {
                    if key == "aria-selected" {
                        None
                    } else {
                        Some((key, sanitize_aria_selected(value)))
                    }
                })
                .collect(),
        ),
        Value::Array(values) => {
            Value::Array(values.into_iter().map(sanitize_aria_selected).collect())
        }
        _ => value,
    }
}

fn sanitize_aria_controls(value: Value) -> Value {
    sanitize_aria_controls_in_tabview(value, false)
}

pub fn sanitize_tabview_aria(value: Value) -> Value {
    let value = sanitize_aria_controls(value);
    sanitize_aria_selected(value)
}
