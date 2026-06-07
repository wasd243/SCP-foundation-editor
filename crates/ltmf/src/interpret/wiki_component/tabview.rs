use serde_json::Value;

use crate::interpret::{
    text::{interpret_text_content, patch_wiki_component_content},
    utils::{get_intercepted_content::get_intercepted_content, get_types::has_type},
};

pub(super) fn interpret_tabview(node: &Value, output: String) -> Result<String, String> {
    if !is_tabview(node) {
        return Ok(output);
    }

    let tabs = tab_titles(node);
    let contents = tab_contents(node)?;
    let output = tabs
        .iter()
        .enumerate()
        .map(|(index, tab)| {
            let content = contents.get(index).cloned().unwrap_or_default();
            format!("[[tab {tab}]]\n{content}\n[[/tab]]")
        })
        .collect::<Vec<_>>()
        .join("\n");

    Ok(format!("[[tabview]]\n{output}\n[[/tabview]]\n"))
}

pub(super) fn is_tabview(node: &Value) -> bool {
    has_type(node, "TabView") || has_type(node, "tabView")
}

fn tab_titles(node: &Value) -> Vec<String> {
    node.get("content")
        .and_then(Value::as_array)
        .and_then(|content| {
            content
                .iter()
                .find(|node| has_type(node, "TabViewButtonList"))
        })
        .and_then(|button_list| button_list.get("content"))
        .and_then(Value::as_array)
        .map(|tabs| {
            tabs.iter()
                .filter(|tab| has_type(tab, "Tab"))
                .map(|tab| get_intercepted_content(tab, interpret_text_content))
                .collect()
        })
        .unwrap_or_default()
}

fn tab_contents(node: &Value) -> Result<Vec<String>, String> {
    node.get("content")
        .and_then(Value::as_array)
        .and_then(|content| {
            content
                .iter()
                .find(|node| has_type(node, "TabViewContentList"))
        })
        .and_then(|content_list| content_list.get("content"))
        .and_then(Value::as_array)
        .map(|contents| {
            contents
                .iter()
                .filter(|content| has_type(content, "TabViewContent"))
                .map(patch_wiki_component_content)
                .collect()
        })
        .unwrap_or_else(|| Ok(Vec::new()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn parses_paragraph_inside_tab_content() {
        let node = json!({
            "type": "tabView",
            "content": [
                {
                    "type": "TabViewButtonList",
                    "content": [
                        {
                            "type": "Tab",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "tab title"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "TabViewContentList",
                    "content": [
                        {
                            "type": "TabViewContent",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "tab content"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        });

        assert_eq!(
            interpret_tabview(&node, String::new()).unwrap(),
            "[[tabview]]\n[[tab tab title]]\ntab content\n[[/tab]]\n[[/tabview]]\n"
        );
    }
}
