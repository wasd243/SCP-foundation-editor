use serde_json::{Map, Value};

pub(super) fn is_tabview(map: &Map<String, Value>) -> bool {
    map.get("attrs")
        .and_then(|attrs| attrs.get("class"))
        .and_then(Value::as_str)
        .is_some_and(|class| class.split_whitespace().any(|class| class == "wj-tabs"))
}
