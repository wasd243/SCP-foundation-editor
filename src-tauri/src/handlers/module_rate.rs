use std::fs;

const MODULE_RATE_TEMP_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/module_rate_status.txt");

#[tauri::command]
pub fn read_module_rate_temp() -> String {
    fs::read_to_string(MODULE_RATE_TEMP_PATH).unwrap()
}
