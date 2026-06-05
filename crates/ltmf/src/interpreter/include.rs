mod generator;
mod search;
mod variable_loader;

use rusqlite::Connection;
use serde_json::Value;

pub fn interpret_include(index: usize, node: &Value) -> Result<String, String> {
    let include_name = node
        .get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(|html_attrs| html_attrs.get("data-editor-include"))
        .and_then(Value::as_str)
        .unwrap_or("unknown");

    let connection = Connection::open("include.db").map_err(|error| error.to_string())?;
    variable_loader::load_variables(&connection)?;
    let include_variables = search::search_include_variables(&connection, include_name)?;

    // PLACEHOLDER
    Ok(format!(
        "[include:{index}] {include_name} {include_variables:?}"
    ))
}
