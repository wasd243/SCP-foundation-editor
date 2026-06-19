use std::fs;
use serde_json::Value;

const OUTPUT_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../temp/dev_output.json");

#[tauri::command]
pub fn log_and_write_json(json: Value) {
    fs::write(OUTPUT_PATH, json.to_string()).unwrap();
}
