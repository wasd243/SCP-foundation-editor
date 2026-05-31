// This function will normalize has attrs/marks Newline type into normal Newline
use serde_json::Value;

pub fn normalize_new_line_marks(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            let is_new_line = map
                .get("type")
                .and_then(Value::as_str)
                == Some("NewLine");

            if is_new_line {
                map.remove("attrs");
                map.remove("marks");
            }

            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, normalize_new_line_marks(value)))
                    .collect(),
            )
        }
        Value::Array(values) => Value::Array(
            values
                .into_iter()
                .map(normalize_new_line_marks)
                .collect(),
        ),
        _ => value,
    }
}
