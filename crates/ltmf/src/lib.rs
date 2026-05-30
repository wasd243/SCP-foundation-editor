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

    #[test]
    fn test_import_json() {
        let mut json = String::new();

        import_json(&mut json);

        json = export_wikitext(&json).unwrap();

        println!("{json}");
    }
}
