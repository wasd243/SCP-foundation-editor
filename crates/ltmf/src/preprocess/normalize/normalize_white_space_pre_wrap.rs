// This function will normalize
//          {
//           "attrs": {
//             "htmlAttributes": {
//               "style": "white-space: pre-wrap;"
//             },
//             "tagName": "span"
//           }
//         },
// To
//         {
//           "type": "ForceNewLine"
//         },
use serde_json::Value;

pub fn normalize_white_space_pre_wrap(value: Value) -> Value {
    match value {
        Value::Object(map) => {
            let value = Value::Object(map);

            if is_force_new_line(&value) {
                return serde_json::json!({
                    "type": "ForceNewLine"
                });
            }

            match value {
                Value::Object(map) => {
                    let value = Value::Object(
                        map.into_iter()
                            .map(|(key, value)| (key, normalize_white_space_pre_wrap(value)))
                            .collect(),
                    );

                    if is_force_new_line_paragraph(&value) {
                        serde_json::json!({
                            "type": "ForceNewLine"
                        })
                    } else {
                        value
                    }
                }
                _ => value,
            }
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(normalize_white_space_pre_wrap)
                .collect(),
        ),
        _ => value,
    }
}

fn is_force_new_line(value: &Value) -> bool {
    value.get("content").is_none()
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("tagName"))
            .and_then(Value::as_str)
            == Some("span")
        && value
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attributes| html_attributes.get("style"))
            .and_then(Value::as_str)
            == Some("white-space: pre-wrap;")
}

fn is_force_new_line_paragraph(value: &Value) -> bool {
    value.get("type").and_then(Value::as_str) == Some("paragraph")
        && value
            .get("content")
            .and_then(Value::as_array)
            .is_some_and(|content| {
                content.len() == 1
                    && content[0].get("type").and_then(Value::as_str) == Some("ForceNewLine")
            })
}
