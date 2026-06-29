use serde_json::Value;
use std::fs;

static LOG_FILE_PATH: &str = "dev_output.json";

#[tauri::command]
pub fn log_and_write_json(json: Value) {
    fs::write(LOG_FILE_PATH, json.to_string()).unwrap_or_else(|e| panic!("{e}"));
}
