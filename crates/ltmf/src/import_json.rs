// `import_json.rs` is temporarily a test file which hardcoded to `test.json`
// Only for testing purpose, going to be removed after implementation of exporter.
use std::fs;

const JSON_PATH: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/test/json/wrapped_image_test.json"
);

pub fn import_json(json: &mut String) -> Result<(), String> {
    *json = fs::read_to_string(JSON_PATH).map_err(|error| error.to_string())?;
    Ok(())
}
