//! Resolve `@import` rules in CSS, like a C/C++ preprocessor.
//!
//! Two kinds of imports are resolved:
//!
//! - **URL imports** (`@import url("https://...")`) are fetched over HTTP by
//!   [`CssResolver`] and inlined recursively (up to a maximum depth, with a
//!   per-URL cache).
//! - **Local imports** (relative file paths) are inlined by the lightningcss
//!   bundler.
//!
//! If anything fails (network error, parse error, missing file) the input is
//! returned unchanged so the pipeline never drops the CSS.

use lightningcss::bundler::{Bundler, FileProvider};
use lightningcss::stylesheet::{ParserOptions, PrinterOptions, StyleSheet};
use regex::Regex;
use reqwest::Client;
use std::collections::HashMap;
use std::path::Path;
use std::sync::atomic::{AtomicU64, Ordering};
use url::Url;

/// How deep to follow nested url `@import` chains.
const DEFAULT_MAX_DEPTH: u32 = 5;

/// Resolves all `@import` rules in `css`:
/// 1. Comments are stripped via lightningcss, so commented-out `@import`s are
///    not matched by the url resolver.
/// 2. URL imports are fetched and inlined recursively.
/// 3. Remaining local imports are bundled by lightningcss.
///
/// On any failure the (partially resolved) CSS is returned rather than lost.
pub fn resolve_import(css: &str) -> String {
    let css = strip_comments(css);
    let css = resolve_url_imports(&css);

    bundle_css(&css).unwrap_or(css)
}

/// Removes all CSS comments by parsing with lightningcss and re-printing
/// (lightningcss drops comments at parse time). Error recovery is enabled so
/// non-standard tokens (e.g. Wikidot `{$var}` placeholders) don't abort the
/// whole parse. Falls back to the input if parsing or printing fails.
fn strip_comments(css: &str) -> String {
    let options = ParserOptions {
        error_recovery: true,
        ..ParserOptions::default()
    };

    let result = StyleSheet::parse(css, options)
        .map_err(|error| error.to_string())
        .and_then(|stylesheet| {
            stylesheet
                .to_css(PrinterOptions::default())
                .map(|printed| printed.code)
                .map_err(|error| error.to_string())
        });

    result.unwrap_or_else(|_| css.to_string())
}

/// Runs the async [`CssResolver`] on an isolated thread with its own
/// current-thread runtime, so it is safe to call even from within an existing
/// (e.g. Tauri) tokio runtime.
fn resolve_url_imports(css: &str) -> String {
    let owned = css.to_string();
    std::thread::spawn(move || {
        let runtime = match tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
        {
            Ok(runtime) => runtime,
            Err(_) => return owned,
        };
        let mut resolver = CssResolver::new(DEFAULT_MAX_DEPTH);
        runtime.block_on(resolver.resolve(&owned))
    })
    .join()
    .unwrap_or_else(|_| css.to_string())
}

/// Resolves url `@import` rules by fetching their content over HTTP and
/// inlining it recursively.
pub struct CssResolver {
    client: Client,
    cache: HashMap<String, String>, // URL -> CSS content
    max_depth: u32,
}

impl CssResolver {
    /// Creates a resolver that follows nested imports up to `max_depth` levels.
    pub fn new(max_depth: u32) -> Self {
        Self {
            client: Client::new(),
            cache: HashMap::new(),
            max_depth,
        }
    }

    /// Resolves every url `@import` in `css`, replacing each with the fetched
    /// (and recursively resolved) CSS content.
    pub async fn resolve(&mut self, css: &str) -> String {
        self.resolve_at_depth(css, None, 0).await
    }

    async fn resolve_at_depth(&mut self, css: &str, base: Option<Url>, depth: u32) -> String {
        // Stop recursing once the depth budget is exhausted.
        if depth >= self.max_depth {
            return css.to_string();
        }

        // Collect matches up front so `css` is not borrowed across the awaits.
        let matches: Vec<(usize, usize, String)> = import_url_regex()
            .captures_iter(css)
            .filter_map(|caps| {
                let whole = caps.get(0)?;
                let url = caps.name("url")?.as_str().trim().to_string();
                Some((whole.start(), whole.end(), url))
            })
            .collect();

        if matches.is_empty() {
            return css.to_string();
        }

        let mut out = String::new();
        let mut last = 0;
        for (start, end, raw_url) in matches {
            out.push_str(&css[last..start]);
            last = end;

            match self.resolve_one(&raw_url, base.as_ref(), depth).await {
                // Inline the resolved content in place of the `@import`.
                Some(resolved) => out.push_str(&resolved),
                // Keep the original `@import` if it could not be resolved.
                None => out.push_str(&css[start..end]),
            }
        }
        out.push_str(&css[last..]);
        out
    }

    /// Resolves a single `@import` target: absolutize, fetch, then recurse.
    async fn resolve_one(
        &mut self,
        raw_url: &str,
        base: Option<&Url>,
        depth: u32,
    ) -> Option<String> {
        let absolute = absolutize(base, raw_url)?;
        let content = self.fetch(absolute.as_str()).await?;
        // Nested imports resolve relative to the file we just fetched.
        let resolved = Box::pin(self.resolve_at_depth(&content, Some(absolute), depth + 1)).await;
        Some(resolved)
    }

    /// Fetches `url`, returning cached content when available.
    async fn fetch(&mut self, url: &str) -> Option<String> {
        if let Some(cached) = self.cache.get(url) {
            return Some(cached.clone());
        }

        let response = self.client.get(url).send().await.ok()?;
        let text = response.text().await.ok()?;
        self.cache.insert(url.to_string(), text.clone());
        Some(text)
    }
}

/// Matches `@import url(...)` and `@import "..."` forms, capturing the target
/// in the `url` group and consuming the whole statement.
fn import_url_regex() -> Regex {
    Regex::new(r#"(?i)@import\s+(?:url\(\s*['"]?|['"])(?P<url>[^'")]+)['"]?\s*\)?\s*;?"#).unwrap()
}

/// Resolves `raw` against `base`: absolute URLs are used as-is; relative ones
/// are joined onto `base`. Returns `None` if it cannot be turned into a URL.
fn absolutize(base: Option<&Url>, raw: &str) -> Option<Url> {
    match Url::parse(raw) {
        Ok(url) => Some(url),
        Err(url::ParseError::RelativeUrlWithoutBase) => base?.join(raw).ok(),
        Err(_) => None,
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

    /// Drives a future to completion on a temporary current-thread runtime.
    fn block<F: std::future::Future>(future: F) -> F::Output {
        tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .unwrap()
            .block_on(future)
    }

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
    fn test_resolve_import_tolerates_odd_input() {
        // Error recovery normalizes odd input rather than dropping it or
        // panicking; the meaningful tokens survive.
        let out = resolve_import("this is not css {{{");
        assert!(out.contains("this is not css"), "content lost: {out}");
    }

    #[test]
    fn test_import_url_regex_matches_forms() {
        let re = import_url_regex();
        let url = |css: &str| {
            re.captures(css)
                .and_then(|c| c.name("url"))
                .map(|m| m.as_str().to_string())
        };

        assert_eq!(
            url(r#"@import url("https://a/x.css");"#),
            Some("https://a/x.css".to_string())
        );
        assert_eq!(
            url(r#"@import url('https://a/x.css')"#),
            Some("https://a/x.css".to_string())
        );
        assert_eq!(
            url(r#"@import url(https://a/x.css);"#),
            Some("https://a/x.css".to_string())
        );
        assert_eq!(
            url(r#"@import "https://a/x.css";"#),
            Some("https://a/x.css".to_string())
        );
        assert_eq!(url("body { color: red; }"), None);
    }

    #[test]
    fn test_resolve_url_import_from_cache() {
        // Pre-seed the cache so no real network request is made.
        let mut resolver = CssResolver::new(5);
        resolver.cache.insert(
            "https://example.com/a.css".into(),
            ".a { color: red; }".into(),
        );

        let out = block(resolver.resolve(r#"@import url("https://example.com/a.css");"#));
        assert!(!out.contains("@import"), "url import not resolved: {out}");
        assert!(out.contains(".a"));
    }

    #[test]
    fn test_resolve_nested_url_imports_from_cache() {
        let mut resolver = CssResolver::new(5);
        resolver.cache.insert(
            "https://x/parent.css".into(),
            r#"@import url("https://x/child.css"); .p {}"#.into(),
        );
        resolver
            .cache
            .insert("https://x/child.css".into(), ".c {}".into());

        let out = block(resolver.resolve(r#"@import url("https://x/parent.css");"#));
        assert!(
            !out.contains("@import"),
            "nested import not resolved: {out}"
        );
        assert!(out.contains(".p"));
        assert!(out.contains(".c"));
    }

    #[test]
    fn test_resolve_respects_max_depth_zero() {
        // With no depth budget nothing is fetched and the input is unchanged.
        let mut resolver = CssResolver::new(0);
        let input = r#"@import url("https://x/a.css");"#;
        assert_eq!(block(resolver.resolve(input)), input);
    }

    #[test]
    fn test_resolve_no_url_import_unchanged() {
        let mut resolver = CssResolver::new(5);
        let out = block(resolver.resolve(".a { color: red; }"));
        assert_eq!(out, ".a { color: red; }");
    }

    #[test]
    fn test_strip_comments_removes_comments() {
        let css = "/* a comment */\n.a { color: red; /* inline */ }";
        let out = strip_comments(css);
        assert!(!out.contains("/*"), "comment not removed: {out}");
        assert!(out.contains(".a"));
    }

    #[test]
    fn test_strip_comments_drops_commented_import() {
        // A url `@import` hidden inside a comment must not survive, so the url
        // resolver never sees (or fetches) it.
        let css = "/* {$v}/\n@import url(\"https://x/c.css\");\n/{$v} */\n.a { color: red; }";
        let out = strip_comments(css);
        assert!(!out.contains("@import"), "commented import survived: {out}");
        assert!(out.contains(".a"));
    }
}
