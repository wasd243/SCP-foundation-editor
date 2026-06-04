use std::fs;
use std::path::Path;

use regex::Regex;
use rusqlite::{params, Connection};

const RESOURCEPACK_COMPONENTS_PATH: &str = "resourcepack/components/";
const VARIABLE_NAME_CONFIG_TABLE_SQL: &str = include_str!("variable_name_config_table.sql");

pub(super) fn load_variables(connection: &Connection) -> Result<(), String> {
    connection
        .execute_batch(VARIABLE_NAME_CONFIG_TABLE_SQL)
        .map_err(|error| error.to_string())?;

    let components_path = Path::new(RESOURCEPACK_COMPONENTS_PATH);
    if !components_path.exists() {
        return Ok(());
    }

    let variable_regex = Regex::new(r"\{\$[^}]+\}").map_err(|error| error.to_string())?;

    load_variables_from_directory(connection, components_path, &variable_regex)
}

fn load_variables_from_directory(
    connection: &Connection,
    directory: &Path,
    variable_regex: &Regex,
) -> Result<(), String> {
    let entries = fs::read_dir(directory).map_err(|error| error.to_string())?;

    for entry in entries {
        let entry = entry.map_err(|error| error.to_string())?;
        let path = entry.path();

        if path.is_dir() {
            load_variables_from_directory(connection, &path, variable_regex)?;
        } else if path
            .extension()
            .is_some_and(|extension| extension == "ftml")
        {
            load_variables_from_ftml(connection, &path, variable_regex)?;
        }
    }

    Ok(())
}

fn load_variables_from_ftml(
    connection: &Connection,
    path: &Path,
    variable_regex: &Regex,
) -> Result<(), String> {
    let content = fs::read_to_string(path).map_err(|error| error.to_string())?;
    let include_name = extract_include_name(&content)
        .ok_or_else(|| format!("missing data-editor-include in {}", path.display()))?;

    for variable_match in variable_regex.find_iter(&content) {
        connection
            .execute(
                "INSERT INTO include_map (include_name, include_variable, pm_json) VALUES (?1, ?2, ?3)",
                params![include_name, variable_match.as_str(), ""],
            )
            .map_err(|error| error.to_string())?;
    }

    Ok(())
}

fn extract_include_name(content: &str) -> Option<&str> {
    let attribute_name = "data-editor-include=";
    let attribute_start = content.find(attribute_name)? + attribute_name.len();
    let attribute_value = content.get(attribute_start..)?;
    let mut chars = attribute_value.chars();
    let quote = chars.next()?;

    if quote != '"' && quote != '\'' {
        return None;
    }

    let value_start = attribute_start + quote.len_utf8();
    let value = content.get(value_start..)?;
    let value_end = value.find(quote)?;

    value.get(..value_end)
}
