use serde_json::{Map, Value};

pub(super) fn adapt_image_block(value: Value) -> Value {
    match value {
        Value::Object(map) if is_image_block_include(&map) => {
            Value::Object(normalize_image_block_include(map))
        }
        Value::Object(map) => Value::Object(
            map.into_iter()
                .map(|(key, value)| (key, adapt_image_block(value)))
                .collect(),
        ),
        Value::Array(values) => Value::Array(values.into_iter().map(adapt_image_block).collect()),
        _ => value,
    }
}

fn normalize_image_block_include(mut map: Map<String, Value>) -> Map<String, Value> {
    normalize_image_block_align(&mut map);

    if let Some(content) = map.get_mut("content").and_then(Value::as_array_mut) {
        for child in content {
            *child = normalize_image_block_child(std::mem::take(child));
        }
    }

    map
}

fn normalize_image_block_child(value: Value) -> Value {
    match value {
        Value::Object(mut map) if is_image_node(&map) => {
            rename_image_src_to_name(&mut map);
            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, adapt_image_block(value)))
                    .collect(),
            )
        }
        Value::Object(mut map) if is_image_caption_node(&map) => {
            map.insert("type".to_string(), Value::String("caption".to_string()));
            map.remove("attrs");
            Value::Object(
                map.into_iter()
                    .map(|(key, value)| (key, adapt_image_block(value)))
                    .collect(),
            )
        }
        value => adapt_image_block(value),
    }
}

fn is_image_block_include(map: &Map<String, Value>) -> bool {
    map.get("type").and_then(Value::as_str) == Some("Include")
        && map
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attrs| html_attrs.get("data-editor-include"))
            .and_then(Value::as_str)
            == Some("component:image-block")
}

fn normalize_image_block_align(map: &mut Map<String, Value>) {
    let Some(class) = map
        .get("attrs")
        .and_then(|attrs| attrs.get("htmlAttributes"))
        .and_then(|html_attrs| html_attrs.get("class"))
        .and_then(Value::as_str)
        .and_then(extract_align)
    else {
        return;
    };

    if let Some(class_value) = map
        .get_mut("attrs")
        .and_then(Value::as_object_mut)
        .and_then(|attrs| attrs.get_mut("htmlAttributes"))
        .and_then(Value::as_object_mut)
        .and_then(|html_attrs| html_attrs.get_mut("class"))
    {
        *class_value = Value::String(class.to_string());
    }
}

fn extract_align(class: &str) -> Option<&'static str> {
    if class.split_whitespace().any(|token| token == "alignright") {
        Some("right")
    } else if class.split_whitespace().any(|token| token == "alignleft") {
        Some("left")
    } else if class.split_whitespace().any(|token| token == "aligncenter") {
        Some("center")
    } else {
        None
    }
}

fn is_image_node(map: &Map<String, Value>) -> bool {
    map.get("type").and_then(Value::as_str) == Some("image")
}

fn rename_image_src_to_name(map: &mut Map<String, Value>) {
    let Some(attrs) = map.get_mut("attrs").and_then(Value::as_object_mut) else {
        return;
    };

    if let Some(src) = attrs.remove("src") {
        attrs.insert("name".to_string(), src);
    }
}

fn is_image_caption_node(map: &Map<String, Value>) -> bool {
    map.get("type").and_then(Value::as_str) == Some("wjBlockTag")
        && map
            .get("attrs")
            .and_then(|attrs| attrs.get("htmlAttributes"))
            .and_then(|html_attrs| html_attrs.get("class"))
            .and_then(Value::as_str)
            .is_some_and(|class| class.split_whitespace().any(|token| token == "scp-image-caption"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn normalizes_editor_image_block_to_include_variable_names() {
        let value = json!({
            "attrs": {
                "htmlAttributes": {
                    "class": "image-container alignright",
                    "data-editor-export": "include",
                    "data-editor-include": "component:image-block",
                    "style": "width:200px"
                },
                "tagName": "div"
            },
            "content": [
                { "type": "paragraph" },
                {
                    "attrs": {
                        "src": "https://scp-wiki.wdfiles.com/local--files/theme%3Abasalt/basalt_scp_logo-for_lightmode.svg"
                    },
                    "type": "image"
                },
                {
                    "attrs": {
                        "htmlAttributes": {
                            "class": "scp-image-caption alignright"
                        },
                        "tagName": "div"
                    },
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
                    "type": "wjBlockTag"
                }
            ],
            "type": "Include"
        });

        let adapted = adapt_image_block(value);

        assert_eq!(
            adapted.pointer("/attrs/htmlAttributes/class"),
            Some(&json!("right"))
        );
        assert_eq!(
            adapted.pointer("/content/1/attrs/name"),
            Some(&json!("https://scp-wiki.wdfiles.com/local--files/theme%3Abasalt/basalt_scp_logo-for_lightmode.svg"))
        );
        assert!(adapted.pointer("/content/1/attrs/src").is_none());
        assert_eq!(adapted.pointer("/content/2/type"), Some(&json!("caption")));
        assert!(adapted.pointer("/content/2/attrs").is_none());
        assert_eq!(
            adapted.pointer("/content/2/content/0/content/0/text"),
            Some(&json!("image preview test"))
        );

        println!("{:#?}", adapted);
    }
}

