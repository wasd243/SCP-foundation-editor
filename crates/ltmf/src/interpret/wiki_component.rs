mod alignments;
mod code;
mod collapsible;
mod div;
pub(crate) mod footnote;
mod image;
mod note;
mod table;
mod tabview;
mod user;

use serde_json::Value;

use crate::interpret::{
    utils::get_types::node_type,
    wiki_component::{
        alignments::{
            interpret_align_center, interpret_align_left, interpret_align_right, is_align_center,
            is_align_left, is_align_right,
        },
        code::{interpret_code, is_code},
        collapsible::interpret_collapsible,
        footnote::interpret_footnote,
        image::{interpret_image, is_image},
        note::{interpret_note, is_note},
        table::{interpret_table, is_table},
        tabview::{interpret_tabview, is_tabview},
        user::{interpret_user, is_user},
    },
};

// TODO:
// Investigate whether nested block children with multiple
// paragraph nodes preserve paragraph boundaries correctly.
//
// Not reproducible in current tests.
pub fn interpret_wiki_component(_index: usize, node: &Value) -> Result<String, String> {
    let content = interpret_footnote(node, String::new())?;
    let content = interpret_collapsible(node, content)?;
    let content = interpret_tabview(node, content)?;
    let content = interpret_note(node, content)?;
    let content = interpret_image(node, content)?;
    let content = interpret_table(node, content)?;
    let content = interpret_user(node, content)?;
    let content = interpret_code(node, content)?;
    let content = interpret_align_left(node, content)?;
    let content = interpret_align_center(node, content)?;
    let content = interpret_align_right(node, content)?;

    Ok(content)
}

pub(crate) fn is_wiki_component_node(node: &Value) -> bool {
    is_align_left(node)
        || is_align_right(node)
        || is_align_center(node)
        || is_tabview(node)
        || is_note(node)
        || is_image(node)
        || is_table(node)
        || is_user(node)
        || is_code(node)
        // This matches! macro only for identifier
        // Going to be removed for future implementation
        || matches!(node_type(node), Some("Collapsible" | "Footnote"))
}
