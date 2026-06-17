//! Resolve `@import` rules in CSS, like a C/C++ preprocessor.
//!
//! Uses the lightningcss bundler to inline every resolvable `@import` into a
//! single style sheet, so the resulting CSS contains no local `@import`.
//! Remote (`http(s)://`) imports cannot be fetched from disk and are left in
//! place by the bundler.

use lightningcss::bundler::{Bundler, FileProvider};
use lightningcss::stylesheet::{ParserOptions, PrinterOptions};
use std::path::Path;
use std::sync::atomic::{AtomicU64, Ordering};

/// Resolves all `@import` rules in `css`, inlining them so the returned CSS
/// contains no resolvable `@import`.
///
/// The bundler is file-based, so the CSS is written to a temporary entry file
/// first; relative `@import`s resolve against the temp directory. If bundling
/// fails (e.g. a parse error or a missing import) the input is returned
/// unchanged so the pipeline never drops the CSS.
pub fn resolve_import(css: &str) -> String {
    match bundle_css(css) {
        Ok(bundled) => bundled,
        Err(_) => css.to_string(),
    }
}

/// Writes `css` to a unique temporary entry file and bundles it.
fn bundle_css(css: &str) -> Result<String, String> {
    static COUNTER: AtomicU64 = AtomicU64::new(0);
    let unique = COUNTER.fetch_add(1, Ordering::Relaxed);
    let entry = std::env::temp_dir().join(format!(
        "wiki_css_resolve_import_{}_{unique}.css",
        std::process::id()
    ));

    std::fs::write(&entry, css).map_err(|error| error.to_string())?;
    let result = bundle_entry(&entry);
    let _ = std::fs::remove_file(&entry);
    result
}

/// Bundles the CSS file at `entry`, inlining its local `@import` dependencies,
/// and returns the printed CSS.
fn bundle_entry(entry: &Path) -> Result<String, String> {
    let fs = FileProvider::new();
    let mut bundler = Bundler::new(&fs, None, ParserOptions::default());
    let stylesheet = bundler.bundle(entry).map_err(|error| error.to_string())?;
    let printed = stylesheet
        .to_css(PrinterOptions::default())
        .map_err(|error| error.to_string())?;
    Ok(printed.code)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_resolve_import_inlines_local() {
        // `import_main.css` does `@import "import_child.css";`. After resolving,
        // the child's rules are inlined and no `@import` remains.
        let entry = Path::new(concat!(env!("CARGO_MANIFEST_DIR"), "/test/import_main.css"));
        let out = bundle_entry(entry).unwrap();

        assert!(!out.contains("@import"), "import was not resolved: {out}");
        assert!(out.contains(".child"), "child rule missing: {out}");
        assert!(out.contains(".main"), "main rule missing: {out}");
    }

    #[test]
    fn test_resolve_import_no_import_passthrough() {
        let out = resolve_import(".a { color: red; }");
        assert!(!out.contains("@import"));
        assert!(out.contains(".a"));
    }

    #[test]
    fn test_resolve_import_invalid_css_falls_back() {
        // Not parseable as a bundle entry on its own terms; the input is
        // returned unchanged rather than lost.
        let input = "this is not css {{{";
        assert_eq!(resolve_import(input), input);
    }
}
