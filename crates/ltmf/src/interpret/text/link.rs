use crate::interpret::utils::get_marks::get_marks_by_type;
use serde_json::Value;

pub(super) fn interpret_link_text(node: &Value, output: String) -> Result<String, String> {
    let Some(href) = link_href(node) else {
        return Ok(output);
    };

    if is_internal_href(href) {
        return Ok(format_internal_link(href, &output));
    }

    Ok(format!("[{href} {output}]"))
}

fn is_internal_href(href: &str) -> bool {
    href.starts_with('/') && !href.starts_with("http://") && !href.starts_with("https://")
}

fn format_internal_link(href: &str, output: &str) -> String {
    if output.is_empty() {
        format!("[[[ {href} ]]]")
    } else {
        format!("[[[ {href} | {output} ]]]")
    }
}

fn link_href(node: &Value) -> Option<&str> {
    get_marks_by_type(node, "link")
        .into_iter()
        .find_map(|mark| mark.get("attrs")?.get("href")?.as_str())
}
