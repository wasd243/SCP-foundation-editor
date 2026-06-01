use serde_json::Value;

pub fn get_marks(node: &Value) -> Vec<&Value> {
    let mut marks = Vec::new();
    collect_marks(node, &mut marks);
    marks
}

pub fn get_marks_by_type<'a>(node: &'a Value, mark_type: &str) -> Vec<&'a Value> {
    get_marks(node)
        .into_iter()
        .filter(|mark| mark.get("type").and_then(Value::as_str) == Some(mark_type))
        .collect()
}

#[allow(dead_code)]
pub fn get_mark_types(node: &Value) -> Vec<&str> {
    get_marks(node)
        .into_iter()
        .filter_map(|mark| mark.get("type").and_then(Value::as_str))
        .collect()
}

pub fn has_mark(node: &Value, mark_type: &str) -> bool {
    get_marks(node)
        .into_iter()
        .any(|mark| mark.get("type").and_then(Value::as_str) == Some(mark_type))
}

fn collect_marks<'a>(node: &'a Value, marks: &mut Vec<&'a Value>) {
    match node {
        Value::Object(map) => {
            if let Some(values) = map.get("marks").and_then(Value::as_array) {
                marks.extend(values);
            }

            for value in map.values() {
                collect_marks(value, marks);
            }
        }
        Value::Array(values) => {
            for value in values {
                collect_marks(value, marks);
            }
        }
        _ => {}
    }
}
