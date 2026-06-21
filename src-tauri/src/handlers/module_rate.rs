use crate::utils::path::temp_dir;
use std::fs;

#[tauri::command]
pub fn read_module_rate_temp() -> Result<String, String> {
    fs::read_to_string(temp_dir().join("module_rate_status.txt")).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn rewrite_module_rate_temp(status: &str, alignment: &str) -> Result<(), String> {
    fs::write(
        temp_dir().join("module_rate_status.txt"),
        format!("{status}\n{alignment}"),
    )
        .map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_read_module_rate_temp() {
        let temp = read_module_rate_temp().unwrap();
        println!("{}", temp);
    }

    #[test]
    fn test_rewrite_module_rate_temp() {
        let temp = read_module_rate_temp().unwrap();

        rewrite_module_rate_temp("MODULE_RATE=TRUE", "ALIGNMENTS=LEFT").unwrap();
        println!("{temp}")
    }
}
