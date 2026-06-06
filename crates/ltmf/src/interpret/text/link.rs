use serde_json::Value;

use crate::interpret::utils::get_marks::get_marks_by_type;

pub(super) fn interpret_link_text(node: &Value, output: String) -> Result<String, String> {
    let Some(href) = link_href(node) else {
        return Ok(output);
    };

    Ok(format!("[{href} {output}]"))
}

fn link_href(node: &Value) -> Option<&str> {
    get_marks_by_type(node, "link")
        .into_iter()
        .find_map(|mark| mark.get("attrs")?.get("href")?.as_str())
}
