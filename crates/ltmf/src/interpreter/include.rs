mod generator;
mod search;
mod variable_loader;

use rusqlite::Connection;
use serde_json::Value;
use std::fs;

const INCLUDE_DB_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/cache/include.db");
const CACHE_DIR: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/cache");

pub fn interpret_include(_index: usize, node: &Value) -> Result<String, String> {
    let include_name = node
        .get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(|html_attrs| html_attrs.get("data-editor-include"))
        .and_then(Value::as_str)
        .unwrap_or("unknown");

    fs::create_dir_all(CACHE_DIR).map_err(|error| error.to_string())?;
    let connection = Connection::open(INCLUDE_DB_PATH).map_err(|error| error.to_string())?;
    variable_loader::load_variables(&connection)?;
    let include_variables = search::search_include_variables(&connection, include_name)?;

    Ok(generator::generate_include(
        include_name,
        &include_variables,
        node,
    ))
}
