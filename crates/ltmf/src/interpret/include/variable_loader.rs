use std::fs;
use std::path::Path;

use regex::Regex;
use rusqlite::{Connection, OptionalExtension, params};

const RESOURCEPACK_INCLUDES_PATH: &str =
    concat!(env!("CARGO_MANIFEST_DIR"), "/../../resourcepack/includes/");
const VARIABLE_NAME_CONFIG_TABLE_SQL: &str = include_str!("variable_name_config_table.sql");

pub(super) fn load_variables(connection: &Connection) -> Result<(), String> {
    let (create_table_sql, insert_variable_sql, search_existing_variable_sql) =
        split_variable_sql()?;

    connection
        .execute_batch(create_table_sql)
        .map_err(|error| error.to_string())?;

    let includes_path = Path::new(RESOURCEPACK_INCLUDES_PATH);
    if !includes_path.exists() {
        return Ok(());
    }

    let variable_regex = Regex::new(r"\{\$[^}]+\}").map_err(|error| error.to_string())?;

    load_variables_from_directory(
        connection,
        includes_path,
        &variable_regex,
        &insert_variable_sql,
        &search_existing_variable_sql,
    )
}

fn split_variable_sql() -> Result<(&'static str, String, String), String> {
    let statements = VARIABLE_NAME_CONFIG_TABLE_SQL
        .split(';')
        .map(str::trim)
        .filter(|statement| !statement.is_empty())
        .collect::<Vec<_>>();

    if statements.len() < 3 {
        return Err("missing include_map SQL statements".to_string());
    }

    Ok((
        statements[0],
        format!("{};", statements[1]),
        format!("{};", statements[2]),
    ))
}

fn load_variables_from_directory(
    connection: &Connection,
    directory: &Path,
    variable_regex: &Regex,
    insert_variable_sql: &str,
    search_existing_variable_sql: &str,
) -> Result<(), String> {
    let entries = fs::read_dir(directory).map_err(|error| error.to_string())?;

    for entry in entries {
        let entry = entry.map_err(|error| error.to_string())?;
        let path = entry.path();

        if path.is_dir() {
            load_variables_from_directory(
                connection,
                &path,
                variable_regex,
                insert_variable_sql,
                search_existing_variable_sql,
            )?;
        } else if path
            .extension()
            .is_some_and(|extension| extension == std::ffi::OsStr::new("ftml"))
        {
            load_variables_from_ftml(
                connection,
                &path,
                variable_regex,
                insert_variable_sql,
                search_existing_variable_sql,
            )?;
        }
    }

    Ok(())
}

fn load_variables_from_ftml(
    connection: &Connection,
    path: &Path,
    variable_regex: &Regex,
    insert_variable_sql: &str,
    search_existing_variable_sql: &str,
) -> Result<(), String> {
    let content = fs::read_to_string(path).map_err(|error| error.to_string())?;
    let variables = variable_regex
        .find_iter(&content)
        .map(|variable_match| variable_match.as_str())
        .collect::<Vec<_>>();

    if variables.is_empty() {
        return Ok(());
    }

    let include_name = extract_include_name(&content)
        .ok_or_else(|| format!("missing data-editor-include in {}", path.display()))?;

    for variable in variables {
        if include_variable_exists(
            connection,
            search_existing_variable_sql,
            include_name,
            variable,
        )? {
            continue;
        }

        connection
            .execute(insert_variable_sql, params![include_name, variable, ""])
            .map_err(|error| error.to_string())?;
    }

    Ok(())
}

// Returns true if the same include_name and include_variable
// already exist in the database.
fn include_variable_exists(
    connection: &Connection,
    search_existing_variable_sql: &str,
    include_name: &str,
    include_variable: &str,
) -> Result<bool, String> {
    connection
        .query_row(
            search_existing_variable_sql,
            params![include_name, include_variable],
            |_| Ok(()),
        )
        .optional()
        .map(|result| result.is_some())
        .map_err(|error| error.to_string())
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn resourcepack_include_path_matches_existing_layout() {
        let includes_path = Path::new(RESOURCEPACK_INCLUDES_PATH);

        assert!(
            includes_path.exists(),
            "resourcepack include variables should be loaded from {}",
            includes_path.display()
        );
    }

    #[test]
    fn extracts_include_name_from_ftml_attribute() {
        let content = r#"[[div data-editor-include="component:image-block"]]"#;

        assert_eq!(extract_include_name(content), Some("component:image-block"));
    }

    #[test]
    fn loads_variables_from_resourcepack_includes() {
        let connection = Connection::open_in_memory().unwrap();

        load_variables(&connection).unwrap();
        load_variables(&connection).unwrap();

        let variables =
            super::super::search::search_include_variables(&connection, "component:image-block")
                .unwrap();

        assert_eq!(
            variables,
            vec!["{$align}", "{$caption}", "{$link}", "{$name}", "{$width}"]
        );
    }
}
