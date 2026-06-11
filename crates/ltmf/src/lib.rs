// This module is public for `src-tauri` to use.
pub mod ftml_fmt;
mod interpret;
mod merge;
mod preprocess;

#[cfg(test)]
mod import_json;

pub use ftml_fmt::ftml_fmt;
pub use interpret::interpret;
pub use merge::merge_final_output;
pub use preprocess::preprocess;

/// Quick export function
pub fn export_wikitext(json: &str) -> Result<String, String> {
    let json = preprocess(json)?;
    let json = interpret(&json)?;
    let json = ftml_fmt(&json);
    merge_final_output(json).map_err(|error| error.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::import_json::import_json;

    #[test]
    fn test_export() -> Result<(), String> {
        let mut json = String::new();
        import_json(&mut json)?;
        export_wikitext(&json)?;
        Ok(())
    }
}
