//! Tauri commands for the "Ignored lines" setting.
//!
//! The frontend owns parsing/validation/merging and sends a canonical list of
//! tokens (`"7"` for a single line, `"1-10"` for a range). These commands persist
//! that list to / read it from `config_dir()/ignore_lines.json`. Writing
//! defensively re-validates each token so a malformed payload can never corrupt
//! the metadata file.

use crate::utils::path::{read_ignore_lines, write_ignore_lines};

/// Read the saved ignored-line tokens for the settings UI.
#[tauri::command]
pub fn read_ignore_lines_metadata() -> Result<Vec<String>, String> {
    Ok(read_ignore_lines())
}

/// Persist the ignored-line tokens. Each must be `N` or `X-Y` with positive
/// integers and `Y >= X`; an invalid token aborts the write unchanged.
#[tauri::command]
pub fn write_ignore_lines_metadata(lines: Vec<String>) -> Result<(), String> {
    for token in &lines {
        validate_token(token)?;
    }
    write_ignore_lines(&lines)
}

/// Validate a single token: `N` or `X-Y`, positive integers, `Y >= X`.
fn validate_token(token: &str) -> Result<(), String> {
    let malformed = || format!("Invalid line entry: {token:?}");

    match token.split_once('-') {
        Some((start, end)) => {
            let start: u32 = start.parse().map_err(|_| malformed())?;
            let end: u32 = end.parse().map_err(|_| malformed())?;
            if start < 1 {
                return Err("Line numbers start at 1.".into());
            }
            if end < start {
                return Err(format!("Range {token:?} must go low to high."));
            }
            Ok(())
        }
        None => {
            let n: u32 = token.parse().map_err(|_| malformed())?;
            if n < 1 {
                return Err("Line numbers start at 1.".into());
            }
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::validate_token;

    #[test]
    fn accepts_single_and_range() {
        assert!(validate_token("7").is_ok());
        assert!(validate_token("1-10").is_ok());
    }

    #[test]
    fn rejects_malformed_zero_and_backwards() {
        assert!(validate_token("abc").is_err());
        assert!(validate_token("0").is_err());
        assert!(validate_token("10-1").is_err());
        assert!(validate_token("1-").is_err());
        assert!(validate_token("-5").is_err());
    }
}
