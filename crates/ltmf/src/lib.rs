mod import_json;
mod normalizer;

use import_json::import_json;

use normalizer::preprocess::sanitize::{
    sanitize_null::sanitize_null,
    sanitize_empty_attrs::sanitize_empty_attrs,
};

use serde_json::Value;

pub fn export_wikitext(json: &str) -> Result<String, String> {
    let mut json = json.to_string();
    import_json(&mut json);

    let json_value: Value = serde_json::from_str(&json).map_err(|error| error.to_string())?;

    let sanitized_json = sanitize_null(&json_value);
    let sanitized_json = sanitize_empty_attrs(&sanitized_json);

    let json = serde_json::to_string_pretty(&sanitized_json).map_err(|error| error.to_string())?;

    Ok(json)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_import_json() {
        let mut json = String::new();

        import_json(&mut json);

        json = export_wikitext(&json).unwrap();

        println!("{json}");
    }
}
