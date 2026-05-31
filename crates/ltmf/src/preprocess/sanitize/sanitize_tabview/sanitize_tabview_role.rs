use super::is_tabview::is_tabview;
use serde_json::Value;

pub fn sanitize_tabview_role(value: Value) -> Value {
    sanitize_tabview_role_in_tabview(value, false)
}

fn sanitize_tabview_role_in_tabview(value: Value, in_tabview: bool) -> Value {
    match value {
        Value::Object(map) => {
            let in_tabview = in_tabview || is_tabview(&map);

            Value::Object(
                map.into_iter()
                    .filter_map(|(key, value)| {
                        if in_tabview && key == "role" {
                            None
                        } else {
                            Some((key, sanitize_tabview_role_in_tabview(value, in_tabview)))
                        }
                    })
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(|value| sanitize_tabview_role_in_tabview(value, in_tabview))
                .collect(),
        ),
        _ => value,
    }
}
