mod blockquote;
mod bold;
pub(crate) mod color;
mod content_paragraph;
mod empty_paragraph;
mod heading;
mod horizontal_rule;
mod italic;
mod link;
mod monospace;
mod new_line;
mod normal_text;
mod ol;
mod original_text;
mod size;
mod strikethrough;
mod sub;
mod sup;
mod ul;
mod underline;

use serde_json::Value;

use crate::interpret::{
    text::{
        blockquote::{interpret_blockquote, is_blockquote},
        bold::interpret_bold_text,
        color::interpret_color_text,
        content_paragraph::interpret_paragraph_with_contents,
        empty_paragraph::{guard_empty_paragraph, interpret_empty_paragraph},
        heading::interpret_heading,
        horizontal_rule::{interpret_horizontal_rule, is_horizontal_rule},
        italic::interpret_italic_text,
        link::interpret_link_text,
        monospace::interpret_monospace_text,
        new_line::interpret_new_line,
        normal_text::interpret_normal_text,
        ol::{interpret_ol, is_ordered_list},
        original_text::interpret_original_text,
        size::interpret_size_text,
        strikethrough::interpret_strike_through_text,
        sub::interpret_sub_text,
        sup::interpret_sup_text,
        ul::{interpret_ul, is_unordered_list},
        underline::interpret_underline_text,
    },
    utils::{
        get_content::{ContentNode, get_content_nodes},
        get_marks::get_marks,
        get_types::{has_type, node_type},
    },
    wiki_component::{interpret_wiki_component, is_nested_wiki_component_node},
};

pub(super) fn interpret_text(_index: usize, node: &Value) -> Result<String, String> {
    let content = interpret_text_content(node).join("");
    let content = interpret_heading(node, content)?;
    let content = guard_empty_paragraph(content)?;
    let content = interpret_normal_text(node, content)?;
    let content = interpret_paragraph_with_contents(node, content)?;

    Ok(content)
}

/// This function is used to guard against empty paragraphs in the output.
/// Only allow one `\n` between `@@@@`
pub(super) fn guard_output_empty_paragraphs(output: String) -> Result<String, String> {
    guard_empty_paragraph(output)
}

/// Interprets the content of a text node.
pub(crate) fn interpret_text_content(node: &Value) -> Vec<String> {
    get_content_nodes(node, stop_collecting_children)
        .into_iter()
        .filter_map(interpret_content_node)
        .collect()
}

pub(crate) fn patch_wiki_component_text(node: &Value) -> Result<String, String> {
    let content = interpret_text_content(node).join("");
    let content = guard_empty_paragraph(content)?;
    interpret_paragraph_with_contents(node, content)
}

/// Compatibility patch for legacy `wiki_component` nodes.
///
/// The legacy interpreter did not model `wiki_component` as a wrapper node.
/// Its child content was stored under `content`, so empty paragraphs and nested
/// text could not be restored by the normal exporter path.
///
/// This function extracts and serializes that legacy content until the
/// interpreter is fully migrated to wrapper-style components.
pub(crate) fn patch_wiki_component_content(node: &Value) -> Result<String, String> {
    // Historical note:
    //
    // This function exists because the legacy interpreter made wiki_component
    // a standalone grammar node instead of a wrapper.
    //
    // I only discovered this bug while implementing the merger.
    //
    // If you are reading this after removing the legacy interpreter,
    // congratulations. You may delete this function.
    //
    // If you are reading this while adding another patch,
    // my condolences.
    node.get("content")
        .and_then(Value::as_array)
        .map(|content| {
            content
                .iter()
                .map(patch_wiki_component_text)
                .collect::<Result<Vec<_>, _>>()
                .map(|content| trim_trailing_newlines(content.join("")))
        })
        .unwrap_or_else(|| Ok(String::new()))
}

/// This function is used to add `\n` to the end of the `wiki_component` outputs.
pub(crate) fn trim_trailing_newlines(output: String) -> String {
    output.trim_end_matches('\n').to_string()
}

/// Interprets a content node, which can be a text node, a new line node,
/// a blockquote node, a horizontal rule node, a list node, or a nested
/// wiki component node.
///
/// This function is used to match different kinds of text nodes...
/// Temporary is not support wiki_components yet
///
/// Because the ` wiki_components ` module has some issues that MUST need to be refactored.
fn interpret_content_node(content_node: ContentNode<'_>) -> Option<String> {
    let node = content_node.node;

    match node_type(node) {
        Some("text") => Some(
            interpret_text_node(node, content_node.parent_type)
                .unwrap_or_else(|error| format!("ERROR:{error}")),
        ),
        Some("NewLine") => Some(
            interpret_new_line(node, String::new())
                .unwrap_or_else(|error| format!("ERROR:{error}")),
        ),
        Some("paragraph") if is_empty_paragraph_node(node) => Some(
            interpret_empty_paragraph(node, String::new())
                .unwrap_or_else(|error| format!("ERROR:{error}")),
        ),
        Some("paragraph") => None,
        Some(_) if is_blockquote(node) => Some(
            interpret_blockquote(node, String::new())
                .unwrap_or_else(|error| format!("ERROR:{error}")),
        ),
        Some(_) if is_horizontal_rule(node) => Some(
            interpret_horizontal_rule(node, String::new())
                .unwrap_or_else(|error| format!("ERROR:{error}")),
        ),
        Some(_) if is_unordered_list(node) => {
            Some(interpret_ul(node, String::new()).unwrap_or_else(|error| format!("ERROR:{error}")))
        }
        Some(_) if is_ordered_list(node) => {
            Some(interpret_ol(node, String::new()).unwrap_or_else(|error| format!("ERROR:{error}")))
        }
        Some(_) if is_nested_wiki_component_node(node) => {
            Some(interpret_wiki_component(0, node).unwrap_or_else(|error| format!("ERROR:{error}")))
        }
        Some(_) => None,
        None => None,
    }
}

/// Stops collecting children of a node if it is an empty paragraph,
/// blockquote, horizontal rule, unordered list, ordered list, or nested
/// wiki component node.
fn stop_collecting_children(node: &Value) -> bool {
    is_empty_paragraph_node(node)
        || is_blockquote(node)
        || is_horizontal_rule(node)
        || is_unordered_list(node)
        || is_ordered_list(node)
        || is_nested_wiki_component_node(node)
}

fn is_empty_paragraph_node(node: &Value) -> bool {
    has_type(node, "paragraph")
        && node
            .get("content")
            .and_then(Value::as_array)
            .map(|content| content.is_empty())
            .unwrap_or(true)
}

fn interpret_text_node(node: &Value, parent_type: Option<&str>) -> Result<String, String> {
    let text = node
        .get("text")
        .and_then(Value::as_str)
        .ok_or_else(|| "text node expected text".to_string())?
        .to_string();

    let text = match get_marks(node).is_empty() {
        true => interpret_normal_text(node, text),
        false => interpret_marked_text(node, text),
    }?;

    match parent_type {
        Some("paragraph") => interpret_original_text(node, text),
        _ => Ok(text),
    }
}

/// Applies all mark-based inline text interpreters, such as color, bold,
/// italic, underline, and strikethrough.
fn interpret_marked_text(node: &Value, output: String) -> Result<String, String> {
    let output = interpret_color_text(node, output)?;
    let output = interpret_bold_text(node, output)?;
    let output = interpret_italic_text(node, output)?;
    let output = interpret_underline_text(node, output)?;
    let output = interpret_strike_through_text(node, output)?;
    let output = interpret_monospace_text(node, output)?;
    let output = interpret_sup_text(node, output)?;
    let output = interpret_sub_text(node, output)?;
    let output = interpret_link_text(node, output)?;
    let output = interpret_size_text(node, output)?;

    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn patches_wiki_component_content_paragraph() {
        let node = json!({
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "content"
                }
            ]
        });

        assert_eq!(patch_wiki_component_text(&node).unwrap(), "content\n\n");
    }

    #[test]
    fn patches_wiki_component_empty_paragraph() {
        let node = json!({
            "type": "paragraph"
        });

        assert_eq!(patch_wiki_component_text(&node).unwrap(), "@@@@");
    }

    #[test]
    fn guards_empty_paragraphs_inside_wiki_component_content() {
        let node = json!({
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "before"
                },
                {
                    "type": "paragraph"
                },
                {
                    "type": "text",
                    "text": "after"
                }
            ]
        });

        assert_eq!(
            patch_wiki_component_text(&node).unwrap(),
            "before\n@@@@\nafter\n\n"
        );
    }

    #[test]
    fn patches_wiki_component_child_paragraphs() {
        let node = json!({
            "type": "Note",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "content"
                        }
                    ]
                }
            ]
        });

        assert_eq!(patch_wiki_component_content(&node).unwrap(), "content");
    }
}
