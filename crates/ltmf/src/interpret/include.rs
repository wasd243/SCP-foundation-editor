mod generator;
mod search;
mod variable_loader;

use rusqlite::Connection;
use serde_json::Value;
use std::fs;

use crate::paths::temp_dir;

pub fn interpret_include(_index: usize, node: &Value) -> Result<String, String> {
    let include_name = node
        .get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(|html_attrs| html_attrs.get("data-editor-include"))
        .and_then(Value::as_str)
        .unwrap_or("unknown");

    // Cache the include variables in `temp/include.db`.
    let cache_dir = temp_dir();
    fs::create_dir_all(&cache_dir).map_err(|error| error.to_string())?;
    let connection =
        Connection::open(cache_dir.join("include.db")).map_err(|error| error.to_string())?;

    variable_loader::load_variables(&connection)?;
    let include_variables = search::search_include_variables(&connection, include_name)?;

    Ok(generator::generate_include(
        include_name,
        &include_variables,
        node,
    ))
}
