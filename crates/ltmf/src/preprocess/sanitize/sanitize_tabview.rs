use serde_json::Value;

pub mod sanitize_tabview_aria;
pub mod sanitize_tabview_attrs;

use sanitize_tabview_aria::sanitize_tabview_aria;
use sanitize_tabview_attrs::sanitize_tabview_attrs;

pub fn sanitize_tabview(value: Value) -> Value {
    let value = sanitize_tabview_aria(value);
    sanitize_tabview_attrs(&value)
}
