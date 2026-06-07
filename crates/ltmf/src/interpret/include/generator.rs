use serde_json::Value;

const NO_SUCH_INCLUDE_FALLBACK: &str = "EDITOR: NO SUCH INCLUDE IN RESOURCEPACK";

pub(super) fn generate_include(
    include_name: &str,
    include_variables: &[String],
    node: &Value,
) -> String {
    if include_variables.is_empty() {
        return NO_SUCH_INCLUDE_FALLBACK.to_string();
    }

    let mut output = format!("[[include :{include_name}");
    let mut has_variable = false;

    for include_variable in include_variables {
        let variable_name = normalize_include_variable_name(include_variable);
        let Some(variable_value) = find_variable_value(node, variable_name) else {
            continue;
        };

        if variable_value.is_empty() {
            continue;
        }

        if has_variable {
            output.push('|');
        } else {
            output.push(' ');
            has_variable = true;
        }

        output.push_str(variable_name);
        output.push('=');
        output.push_str(&variable_value);
    }

    output.push_str("]] ");
    output.pop();
    output
}

fn normalize_include_variable_name(include_variable: &str) -> &str {
    include_variable
        .trim()
        .strip_prefix("{$")
        .unwrap_or(include_variable)
        .strip_suffix('}')
        .unwrap_or_else(|| {
            include_variable
                .trim()
                .strip_prefix("{$")
                .unwrap_or(include_variable)
        })
        .trim()
}

fn find_variable_value(node: &Value, variable_name: &str) -> Option<String> {
    find_value_by_key(node, variable_name)
        .or_else(|| find_text_by_node_type(node, variable_name))
        .or_else(|| find_value_in_style(node, variable_name))
        .or_else(|| find_adapter_alias_value(node, variable_name))
}

fn find_value_by_key(node: &Value, variable_name: &str) -> Option<String> {
    match node {
        Value::Object(map) => {
            if let Some(value) = map.get(variable_name).and_then(value_to_string) {
                return Some(value);
            }

            map.values()
                .find_map(|value| find_value_by_key(value, variable_name))
        }
        Value::Array(values) => values
            .iter()
            .find_map(|value| find_value_by_key(value, variable_name)),
        _ => None,
    }
}

fn find_text_by_node_type(node: &Value, variable_name: &str) -> Option<String> {
    match node {
        Value::Object(map) => {
            if map.get("type").and_then(Value::as_str) == Some(variable_name) {
                let content = collect_text_content(node);
                if !content.is_empty() {
                    return Some(content);
                }
            }

            map.values()
                .find_map(|value| find_text_by_node_type(value, variable_name))
        }
        Value::Array(values) => values
            .iter()
            .find_map(|value| find_text_by_node_type(value, variable_name)),
        _ => None,
    }
}

fn collect_text_content(node: &Value) -> String {
    match node {
        Value::Object(map) => {
            if let Some(text) = map.get("text").and_then(Value::as_str) {
                return text.to_string();
            }

            map.get("content")
                .and_then(Value::as_array)
                .map(|content| content.iter().map(collect_text_content).collect::<String>())
                .unwrap_or_default()
        }
        Value::Array(values) => values.iter().map(collect_text_content).collect::<String>(),
        _ => String::new(),
    }
}

fn find_value_in_style(node: &Value, variable_name: &str) -> Option<String> {
    match node {
        Value::Object(map) => {
            if let Some(style) = map.get("style").and_then(Value::as_str)
                && let Some(value) = find_style_property(style, variable_name)
            {
                return Some(value.to_string());
            }

            map.values()
                .find_map(|value| find_value_in_style(value, variable_name))
        }
        Value::Array(values) => values
            .iter()
            .find_map(|value| find_value_in_style(value, variable_name)),
        _ => None,
    }
}

fn find_style_property<'a>(style: &'a str, property_name: &str) -> Option<&'a str> {
    style.split(';').find_map(|declaration| {
        let (name, value) = declaration.split_once(':')?;
        (name.trim() == property_name)
            .then(|| value.trim())
            .filter(|value| !value.is_empty())
    })
}

fn find_adapter_alias_value(node: &Value, variable_name: &str) -> Option<String> {
    match variable_name {
        "align" => node
            .pointer("/attrs/htmlAttributes/class")
            .and_then(Value::as_str)
            .map(|value| value.to_string()),
        _ => None,
    }
}

fn value_to_string(value: &Value) -> Option<String> {
    match value {
        Value::String(value) => Some(value.to_string()),
        Value::Number(value) => Some(value.to_string()),
        Value::Bool(value) => Some(value.to_string()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn generates_include_with_matching_resourcepack_variables() {
        let node = json!({
            "attrs": {
                "htmlAttributes": {
                    "class": "right",
                    "data-editor-include": "component:image-block",
                    "style": "width:200px"
                }
            },
            "content": [
                {
                    "attrs": {
                        "name": "example.png"
                    },
                    "type": "image"
                },
                {
                    "content": [
                        {
                            "content": [
                                {
                                    "text": "image preview test",
                                    "type": "text"
                                }
                            ],
                            "type": "paragraph"
                        }
                    ],
                    "type": "caption"
                }
            ],
            "type": "Include"
        });
        let variables = vec![
            "{$align}".to_string(),
            "{$caption}".to_string(),
            "{$link}".to_string(),
            "{$name}".to_string(),
            "{$width}".to_string(),
        ];

        let output = generate_include("component:image-block", &variables, &node);

        assert_eq!(
            output,
            "[[include :component:image-block align=right|caption=image preview test|name=example.png|width=200px]]"
        );
    }

    #[test]
    fn falls_back_when_resourcepack_include_is_missing() {
        let node = json!({ "type": "Include" });

        let output = generate_include("unknown", &[], &node);

        assert_eq!(output, NO_SUCH_INCLUDE_FALLBACK);
    }
}
