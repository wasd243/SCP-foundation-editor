use std::fs;

const MODULE_RATE_TEMP_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../temp/module_rate_status.txt");

#[tauri::command]
pub fn read_module_rate_temp() -> Result<String, String> {
    fs::read_to_string(MODULE_RATE_TEMP_PATH).map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_read_module_rate_temp() {
        let temp = read_module_rate_temp().unwrap();
        println!("{}", temp);
    }
}
