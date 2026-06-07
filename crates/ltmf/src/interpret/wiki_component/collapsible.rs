use regex::Regex;
use serde_json::Value;

use crate::interpret::{text::patch_wiki_component_content, utils::get_types::has_type};

pub(super) fn interpret_collapsible(node: &Value, output: String) -> Result<String, String> {
    if !has_type(node, "Collapsible") {
        return Ok(output);
    }

    let (show, hide) = collapsible_labels(node)?;
    let output = collapsible_content(node)?;

    Ok(format!(
        "[[collapsible show=\"{show}\" hide=\"{hide}\"]]\n{output}\n[[/collapsible]]\n"
    ))
}

fn collapsible_labels(node: &Value) -> Result<(String, String), String> {
    let summary = collapsible_summary(node).unwrap_or_default();
    let regex = Regex::new(r"^\+(.*?)-(.*)$").map_err(|error| error.to_string())?;

    let Some(captures) = regex.captures(&summary) else {
        return Ok((String::new(), String::new()));
    };

    let show = captures
        .get(1)
        .map(|value| value.as_str().to_string())
        .unwrap_or_default();
    let hide = captures
        .get(2)
        .map(|value| value.as_str().to_string())
        .unwrap_or_default();

    Ok((show, hide))
}

fn collapsible_summary(node: &Value) -> Option<String> {
    node.get("content")?
        .as_array()?
        .iter()
        .find(|node| has_type(node, "CollapsibleSummary"))
        .and_then(raw_text_content)
}

fn raw_text_content(node: &Value) -> Option<String> {
    node.get("content")?.as_array().map(|content| {
        content
            .iter()
            .filter_map(|node| node.get("text").and_then(Value::as_str))
            .collect::<String>()
    })
}

fn collapsible_content(node: &Value) -> Result<String, String> {
    node.get("content")
        .and_then(Value::as_array)
        .and_then(|content| {
            content
                .iter()
                .find(|node| has_type(node, "CollapsibleContent"))
        })
        .map(patch_wiki_component_content)
        .unwrap_or_else(|| Ok(String::new()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn parses_paragraph_inside_collapsible_content() {
        let node = json!({
            "type": "Collapsible",
            "content": [
                {
                    "type": "CollapsibleSummary",
                    "content": [
                        {
                            "type": "text",
                            "text": "+open-close"
                        }
                    ]
                },
                {
                    "type": "CollapsibleContent",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "collapsible content"
                                }
                            ]
                        }
                    ]
                }
            ]
        });

        assert_eq!(
            interpret_collapsible(&node, String::new()).unwrap(),
            "[[collapsible show=\"open\" hide=\"close\"]]\ncollapsible content\n[[/collapsible]]\n"
        );
    }
}
