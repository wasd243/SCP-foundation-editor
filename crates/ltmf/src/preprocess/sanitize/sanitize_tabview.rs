use serde_json::Value;

pub mod sanitize_tabview_aria;
pub mod sanitize_tabview_attrs;
pub mod sanitize_tabview_id;
pub mod sanitize_tabview_role;
pub mod sanitize_tabindex;
pub mod is_tabview;

use sanitize_tabview_aria::sanitize_tabview_aria;
use sanitize_tabview_attrs::sanitize_tabview_attrs;
use sanitize_tabview_id::sanitize_tabview_id;
use sanitize_tabview_role::sanitize_tabview_role;
use sanitize_tabindex::sanitize_tabindex;

pub fn sanitize_tabview(value: Value) -> Value {
    let value = sanitize_tabview_aria(value);
    let value = sanitize_tabview_attrs(&value);
    let value = sanitize_tabview_id(value);
    let value = sanitize_tabview_role(value);
    sanitize_tabindex(value)
}
