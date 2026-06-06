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

    for matched in regex.find_iter(&output) {
        let start = matched.start();
        let end = matched.end();

        guarded.push_str(&output[last_end..start]);

        if start > 0 && !output[..start].ends_with('\n') {
            guarded.push('\n');
        }

        guarded.push_str(matched.as_str());

        if end < output.len() && !output[end..].starts_with('\n') {
            guarded.push('\n');
        }

        last_end = end;
    }

    guarded.push_str(&output[last_end..]);

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
