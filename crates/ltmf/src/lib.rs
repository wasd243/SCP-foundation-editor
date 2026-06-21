// This module is public for `src-tauri` to use.
pub mod ftml_fmt;
mod interpret;
mod merge;
pub mod paths;
mod preprocess;

#[cfg(test)]
mod import_json;

pub use ftml_fmt::ftml_fmt;
pub use interpret::interpret;
pub use merge::merge_final_output;
pub use paths::{resourcepack_dir, temp_dir};
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
        // Materialize the dev-tree resourcepack so include variables resolve
        // (mirrors the host's startup copy).
        crate::paths::ensure_test_resourcepack();

        let mut json = String::new();
        import_json(&mut json)?;
        let output = export_wikitext(&json)?;

        // An image-block includes nested inside a `[[div]]` must round-trip as a
        // full `[[include]]` rather than being torn apart into a bare `[[image]]`.
        assert!(
            output.contains(
                "[[include :component:image-block align=left|caption=rust-game|name=https://files.facepunch.com/lewis/1b2911b1/rust-marque.svg|width=200px]]"
            ),
            "nested include was lost from div block:\n{output}"
        );

        Ok(())
    }
}
