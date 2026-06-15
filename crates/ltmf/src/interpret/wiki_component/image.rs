use serde_json::Value;

use crate::interpret::utils::get_types::has_type;

pub(super) fn interpret_image(node: &Value, output: String) -> Result<String, String> {
    if !is_image(node) {
        return Ok(output);
    }

    let src = image_src(node).ok_or_else(|| "image expected attrs.src".to_string())?;
    let options = image_options(node);

    Ok(match image_alignment(node) {
        Some(ImageAlignment::Left) => format!("[[<image {src}{options}]]"),
        Some(ImageAlignment::Right) => format!("[[>image {src}{options}]]"),
        Some(ImageAlignment::Center) => format!("[[=image {src}{options}]]"),
        Some(ImageAlignment::FloatLeft) => format!("[[f<image {src}{options}]]"),
        Some(ImageAlignment::FloatRight) => format!("[[f>image {src}{options}]]"),
        None => format!("[[image {src}{options}]]"),
    })
}

pub(super) fn is_image(node: &Value) -> bool {
    has_type(node, "image")
}

enum ImageAlignment {
    Left,
    Right,
    Center,
    FloatLeft,
    FloatRight,
}

fn image_src(node: &Value) -> Option<&str> {
    node.get("attrs")?.get("src")?.as_str()
}

fn image_options(node: &Value) -> String {
    let Some(style) = node
        .get("attrs")
        .and_then(|attrs| attrs.get("wrapperAttributes"))
        .and_then(|wrapper_attrs| wrapper_attrs.get("style"))
        .and_then(Value::as_str)
    else {
        return String::new();
    };

    let mut options = String::new();

    if let Some(width) = style_value(style, "width") {
        options.push_str(&format!(" width=\"{width}\""));
    }

    if let Some(height) = style_value(style, "height") {
        options.push_str(&format!(" height=\"{height}\""));
    }

    options
}

fn style_value(style: &str, name: &str) -> Option<String> {
    style
        .split(';')
        .map(str::trim)
        .filter(|part| !part.is_empty())
        .find_map(|part| {
            let (key, value) = part.split_once(':')?;
            if key.trim() != name {
                return None;
            }

            let value = value.trim();
            if value.is_empty() {
                None
            } else {
                Some(value.to_string())
            }
        })
}

/// This function is used to identify the alignment of the image.
fn image_alignment(node: &Value) -> Option<ImageAlignment> {
    let class = node
        .get("attrs")?
        .get("wrapperAttributes")?
        .get("class")?
        .as_str()?;

    if class_has_token(class, "floatleft") {
        return Some(ImageAlignment::FloatLeft);
    }

    if class_has_token(class, "floatright") {
        return Some(ImageAlignment::FloatRight);
    }

    if class_has_token(class, "alignleft") {
        return Some(ImageAlignment::Left);
    }

    if class_has_token(class, "alignright") {
        return Some(ImageAlignment::Right);
    }

    if class_has_token(class, "aligncenter") {
        return Some(ImageAlignment::Center);
    }

    None
}

fn class_has_token(class: &str, token: &str) -> bool {
    class.split_whitespace().any(|value| value == token)
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::interpret_image;

    #[test]
    fn interprets_image_width_and_height_from_wrapper_attributes_style() {
        let node = json!({
            "type": "image",
            "attrs": {
                "src": "example.png",
                "wrapperAttributes": {
                    "style": "width: 457px; height: 437px;"
                }
            }
        });

        assert_eq!(
            interpret_image(&node, String::new()).unwrap(),
            r#"[[image example.png width="457px" height="437px"]]"#
        );
    }

    #[test]
    fn interprets_partial_image_style() {
        let node = json!({
            "type": "image",
            "attrs": {
                "src": "example.png",
                "wrapperAttributes": {
                    "style": "width: 457px;"
                }
            }
        });

        assert_eq!(
            interpret_image(&node, String::new()).unwrap(),
            r#"[[image example.png width="457px"]]"#
        );
    }

    #[test]
    fn interprets_floatleft_image() {
        let node = json!({
            "type": "image",
            "attrs": {
                "src": "example.png",
                "wrapperAttributes": {
                    "class": "image-container floatleft"
                }
            }
        });

        assert_eq!(
            interpret_image(&node, String::new()).unwrap(),
            "[[f<image example.png]]"
        );
    }

    #[test]
    fn interprets_floatleft_image_with_width_and_height() {
        let node = json!({
            "type": "image",
            "attrs": {
                "src": "example.png",
                "wrapperAttributes": {
                    "class": "image-container floatleft",
                    "style": "width: 457px; height: 437px;"
                }
            }
        });

        assert_eq!(
            interpret_image(&node, String::new()).unwrap(),
            r#"[[f<image example.png width="457px" height="437px"]]"#
        );
    }

    #[test]
    fn interprets_floatright_image() {
        let node = json!({
            "type": "image",
            "attrs": {
                "src": "example.png",
                "wrapperAttributes": {
                    "class": "image-container floatright"
                }
            }
        });

        assert_eq!(
            interpret_image(&node, String::new()).unwrap(),
            "[[f>image example.png]]"
        );
    }

    #[test]
    fn interprets_floatright_image_with_width_and_height() {
        let node = json!({
            "type": "image",
            "attrs": {
                "src": "example.png",
                "wrapperAttributes": {
                    "class": "image-container floatright",
                    "style": "width: 457px; height: 437px;"
                }
            }
        });

        assert_eq!(
            interpret_image(&node, String::new()).unwrap(),
            r#"[[f>image example.png width="457px" height="437px"]]"#
        );
    }
}
