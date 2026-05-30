mod import_json;
pub mod preprocess;

use preprocess::preprocess;

pub fn export_wikitext(json: &str) -> Result<String, String> {
    preprocess(json)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_export_default_json() {
        let json = export_wikitext("").unwrap();
        let output_path = concat!(env!("CARGO_MANIFEST_DIR"), "/test/json/default.json");

        fs::write(output_path, json).unwrap();

        println!("Pass");
    }
}
