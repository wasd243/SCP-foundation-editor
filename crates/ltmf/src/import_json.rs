// `import_json.rs` is temporarily a test file which hardcoded to `test.json`
use std::fs;

const JSON_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/src/json/test.json");

pub fn import_json(json: &mut String) {
    *json = fs::read_to_string(JSON_PATH).expect("failed to read test.json");
}
