use rusqlite::{params, Connection};

const VARIABLE_NAME_CONFIG_TABLE_SQL: &str = include_str!("variable_name_config_table.sql");

pub(super) fn search_include_variables(
    connection: &Connection,
    include_name: &str,
) -> Result<Vec<String>, String> {
    let search_include_variables_sql = search_include_variables_sql()?;
    let mut statement = connection
        .prepare(&search_include_variables_sql)
        .map_err(|error| error.to_string())?;

    let variables = statement
        .query_map(params![include_name], |row| row.get::<_, String>(0))
        .map_err(|error| error.to_string())?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|error| error.to_string())?;

    Ok(variables)
}

fn search_include_variables_sql() -> Result<String, String> {
    let statement = VARIABLE_NAME_CONFIG_TABLE_SQL
        .split(';')
        .map(str::trim)
        .filter(|statement| !statement.is_empty())
        .nth(3)
        .ok_or_else(|| "missing include variable search SQL".to_string())?;

    Ok(format!("{statement};"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::interpret::include::variable_loader::load_variables;

    #[test]
    fn returns_all_unique_variables_for_matching_include_name() {
        let connection = Connection::open_in_memory().unwrap();

        load_variables(&connection).unwrap();
        load_variables(&connection).unwrap();

        let variables = search_include_variables(&connection, "component:image-block").unwrap();

        assert_eq!(
            variables,
            vec!["{$align}", "{$caption}", "{$link}", "{$name}", "{$width}"]
        );
    }
}
