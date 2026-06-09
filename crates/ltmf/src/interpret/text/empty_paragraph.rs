use regex::Regex;
use serde_json::Value;

use crate::interpret::utils::get_types::has_type;

pub(super) fn interpret_empty_paragraph(node: &Value, output: String) -> Result<String, String> {
    if !is_empty_paragraph(node) {
        return Ok(output);
    }

    Ok("@@@@".to_string())
}

pub(super) fn guard_empty_paragraph(output: String) -> Result<String, String> {
    let regex = Regex::new(r"@@@@").map_err(|error| error.to_string())?;
    let mut guarded = String::with_capacity(output.len());
    let mut last_end = 0;
    let mut found_empty_paragraph = false;

    for matched in regex.find_iter(&output) {
        let start = matched.start();
        let end = matched.end();

        let before = if found_empty_paragraph {
            output[last_end..start].trim_matches('\n')
        } else {
            output[last_end..start].trim_end_matches('\n')
        };

        if found_empty_paragraph && !before.is_empty() && !guarded.ends_with('\n') {
            guarded.push('\n');
        }

        guarded.push_str(before);

        if !guarded.is_empty() && !guarded.ends_with('\n') {
            guarded.push('\n');
        }

        guarded.push_str(matched.as_str());

        last_end = end;
        found_empty_paragraph = true;
    }

    if found_empty_paragraph {
        let after = output[last_end..].trim_start_matches('\n');

        if !after.is_empty() && !guarded.ends_with('\n') {
            guarded.push('\n');
        }

        guarded.push_str(after);
    } else {
        guarded.push_str(&output[last_end..]);
    }

    Ok(guarded)
}

fn is_empty_paragraph(node: &Value) -> bool {
    if !has_type(node, "paragraph") {
        return false;
    }

    node.get("content")
        .and_then(Value::as_array)
        .map(|content| content.is_empty())
        .unwrap_or(true)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_missing_newlines_around_empty_paragraph() {
        assert_eq!(
            guard_empty_paragraph("before@@@@after".to_string()).unwrap(),
            "before\n@@@@\nafter"
        );
    }

    #[test]
    fn collapses_extra_newlines_around_empty_paragraph() {
        assert_eq!(
            guard_empty_paragraph("before\n\n@@@@\n\nafter".to_string()).unwrap(),
            "before\n@@@@\nafter"
        );
    }

    #[test]
    fn keeps_one_newline_between_empty_paragraphs() {
        assert_eq!(
            guard_empty_paragraph("@@@@\n\n@@@@".to_string()).unwrap(),
            "@@@@\n@@@@"
        );
    }

    #[test]
    fn collapses_extra_newlines_between_empty_paragraph_and_content() {
        assert_eq!(
            guard_empty_paragraph("@@@@\n\ncontent\n\n@@@@".to_string()).unwrap(),
            "@@@@\ncontent\n@@@@"
        );
    }
}
