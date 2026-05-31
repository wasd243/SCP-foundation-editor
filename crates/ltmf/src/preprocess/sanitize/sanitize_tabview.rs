use serde_json::Value;

pub mod is_tabview;
pub mod sanitize_tabindex;
pub mod sanitize_tabview_aria;
pub mod sanitize_tabview_attrs;
pub mod sanitize_tabview_hidden;
pub mod sanitize_tabview_id;
pub mod sanitize_tabview_role;

use sanitize_tabindex::sanitize_tabindex;
use sanitize_tabview_aria::sanitize_tabview_aria;
use sanitize_tabview_attrs::sanitize_tabview_attrs;
use sanitize_tabview_hidden::sanitize_tabview_hidden;
use sanitize_tabview_id::sanitize_tabview_id;
use sanitize_tabview_role::sanitize_tabview_role;

pub fn sanitize_tabview(value: Value) -> Value {
    let value = sanitize_tabview_aria(value);
    let value = sanitize_tabview_attrs(&value);
    let value = sanitize_tabview_id(value);
    let value = sanitize_tabview_role(value);
    let value = sanitize_tabindex(value);
    sanitize_tabview_hidden(value)
}
