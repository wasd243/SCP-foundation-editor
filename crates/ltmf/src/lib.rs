mod import_json;
mod normalizer;

use import_json::import_json;

pub fn export_wikitext(json: &str) -> Result<String, String> {
    let mut json = json.to_string();
    import_json(&mut json);

    Ok(json)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_import_json() {
        let mut json = String::new();

        import_json(&mut json);

        println!("{json}");
    }
}
