//! ### Why this module exists:
//!
//! 1. `ftml` footnote parse result in a wired format and not kind to WYSIWYG editor
//! 2. `ProseMirror` already has a footnote plugin
//! 3. The legacy footnote editor and Exporter are NOT reliable and have too many issues
//! 4. Wikitext footnote blocks are easy for regex interceptor and parser implementation
//!
//! ### How it works:
//!
//! 1. Intercept and replace all `[[footnote]](.*?)[[/footnote]]`
//! 2. Change them to `<footnote>(.*?)</footnote>`
//!
//! I know that HTML and wikitext are NOT regex languages, but this part use regex is really simple.
//! Plus, I've intercepted all footnote blocks before parsing.

pub mod footnote_interceptor;
pub mod footnote_parser;
