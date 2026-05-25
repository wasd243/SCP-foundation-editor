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

pub mod module_rate;
pub mod note;
pub mod preprocess_interceptor;
