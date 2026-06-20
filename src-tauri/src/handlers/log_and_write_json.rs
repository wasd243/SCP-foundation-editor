use crate::utils::path::temp_dir;
use serde_json::Value;
use std::fs;

#[tauri::command]
pub fn log_and_write_json(json: Value) {
    fs::write(temp_dir().join("dev_output.json"), json.to_string()).unwrap();
}
