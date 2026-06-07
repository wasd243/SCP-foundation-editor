//! FTML compatibility interceptor layer.
//!
//! Some Wikidot blocks are currently not handled by FTML in the way this
//! editor needs, so they are intercepted before FTML tokenization.
//!
//! Intercepted here:
//! - `[[module rate]]`
//! - `[[note]]NOTE[[/note]]`
//!
//! Already handled by FTML:
//! - `[[footnote]]FOOTNOTE HERE[[/footnote]]`
//! - `[[tabview]][[tab ]]CONTENT[[/tab]][[/tabview]]`
//! - `[[image URL]]`
//! - `[[collapsible show="+" hide="-"]]CONTENT[[/collapsible]]`
//!
//! These FTML-supported blocks do not need Rust interception, but their
//! rendered HTML may still need TypeScript-side DOM replacement so TipTap can
//! recognize them as editor components.
//!
//! Preprocess interceptor:
//! FTML parses wikitext in the following pipeline:
//! preprocessing -> tokenization -> parse
//!
//! However, several malformed patterns may appear after preprocessing,
//! especially when include-expanded wikitext is involved.
//!
//! So this interceptor normalizes the generated wikitext before tokenization.
//!
//! Current fixes:
//! - unresolved variables
//! - malformed newlines (\n)
//!
//! About `[[module CSS]]`:
//!
//! `[[module CSS]]` is parsed by FTML, but its content is not preserved
//! in ProseMirror JSON. Therefore, we do not pass it through the normal
//! interceptor/exporter pipeline.
//!
//! Instead, this interceptor extracts the raw CSS content before it is lost
//! and stores it in the temp temp for the merger/exporter to restore later.

pub mod module_css;
pub mod module_rate;
pub mod note;
pub mod preprocess_interceptor;
pub mod user;
