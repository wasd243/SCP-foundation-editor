use std::fs;
use std::path::Path;

use regex::Regex;
use rusqlite::{params, Connection};

const RESOURCEPACK_INCLUDES_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../resourcepack/includes/");
const VARIABLE_NAME_CONFIG_TABLE_SQL: &str = include_str!("variable_name_config_table.sql");

pub(super) fn load_variables(connection: &Connection) -> Result<(), String> {
    let (create_table_sql, insert_variable_sql) = split_variable_sql()?;

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
    )
}

fn split_variable_sql() -> Result<(&'static str, String), String> {
    let insert_statement_start = "INSERT INTO include_map";
    let (create_table_sql, insert_variable_sql) = VARIABLE_NAME_CONFIG_TABLE_SQL
        .split_once(insert_statement_start)
        .ok_or_else(|| "missing include_map insert statement SQL".to_string())?;

    Ok((
        create_table_sql.trim(),
        format!("{insert_statement_start}{}", insert_variable_sql.trim()),
    ))
}

fn load_variables_from_directory(
    connection: &Connection,
    directory: &Path,
    variable_regex: &Regex,
    insert_variable_sql: &str,
) -> Result<(), String> {
    let entries = fs::read_dir(directory).map_err(|error| error.to_string())?;

    for entry in entries {
        let entry = entry.map_err(|error| error.to_string())?;
        let path = entry.path();

        if path.is_dir() {
            load_variables_from_directory(connection, &path, variable_regex, insert_variable_sql)?;
        } else if path
            .extension()
            .is_some_and(|extension| extension == "ftml")
        {
            load_variables_from_ftml(connection, &path, variable_regex, insert_variable_sql)?;
        }
    }

    Ok(())
}

fn load_variables_from_ftml(
    connection: &Connection,
    path: &Path,
    variable_regex: &Regex,
    insert_variable_sql: &str,
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
        connection
            .execute(insert_variable_sql, params![include_name, variable, ""])
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

        let mut statement = connection
            .prepare(
                "SELECT include_variable FROM include_map WHERE include_name = ?1 ORDER BY include_variable",
            )
            .unwrap();
        let variables = statement
            .query_map(params!["component:image-block"], |row| row.get::<_, String>(0))
            .unwrap()
            .collect::<Result<Vec<_>, _>>()
            .unwrap();

        assert_eq!(variables, vec!["{$align}", "{$caption}", "{$link}", "{$name}", "{$width}"]);
    }
}
