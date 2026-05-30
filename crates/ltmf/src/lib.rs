mod import_json;
pub mod preprocess;

use preprocess::preprocess;

pub fn export_wikitext(json: &str) -> Result<String, String> {
    preprocess(json)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::import_json::import_json;
    use serde_json::Value;
    use std::fs;

    #[test]
    fn test_import_json() {
        let mut json = String::new();

        import_json(&mut json);

        json = export_wikitext(&json).unwrap();

        println!("{json}");
    }

    #[test]
    fn test_sanitize_8() {
        let json = export_wikitext("").unwrap();
        let expected_json =
            fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/test/json/sanitize_11.json"))
                .unwrap();

        let actual: Value = serde_json::from_str(&json).unwrap();
        let expected: Value = serde_json::from_str(&expected_json).unwrap();

        assert_eq!(actual, expected);
        println!("Pass");
    }
}
