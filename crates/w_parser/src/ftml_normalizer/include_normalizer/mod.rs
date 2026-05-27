//! Include normalizer clean parser output for partially filled `[[include]]` tags.
//!
//! FTML supports most Wikidot components, but existing pages sometimes omit
//! include variables that Wikidot tolerates at render time. Those unresolved
//! placeholders can leak into generated HTML and break downstream editor
//! adapters.
//!
//! For example, component image blocks may render with unresolved alignment:
//!
//! ```html
//! <div class="scp-image-block block-{$align}">
//! ```
//!
//! The normalizer converts that to a parser-level default:
//!
//! ```html
//! <div class="scp-image-block block-right">
//! ```
//!
//! The UI htmlAdapter can then map `block-right` to editor-specific classes
//! such as `image-container alignright`.
pub mod component_image_normalizer;
