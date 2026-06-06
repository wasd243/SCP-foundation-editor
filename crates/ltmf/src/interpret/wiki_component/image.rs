use serde_json::Value;

use crate::interpret::utils::get_types::has_type;

pub(super) fn interpret_image(node: &Value, output: String) -> Result<String, String> {
    if !is_image(node) {
        return Ok(output);
    }

    let src = image_src(node).ok_or_else(|| "image expected attrs.src".to_string())?;

    Ok(match image_alignment(node) {
        Some(ImageAlignment::Left) => format!("[[<image {src}]]"),
        Some(ImageAlignment::Right) => format!("[[>image {src}]]"),
        Some(ImageAlignment::Center) => format!("[[=image {src}]]"),
        None => format!("[[image {src}]]"),
    })
}

pub(super) fn is_image(node: &Value) -> bool {
    has_type(node, "image")
}

enum ImageAlignment {
    Left,
    Right,
    Center,
}

fn image_src(node: &Value) -> Option<&str> {
    node.get("attrs")?.get("src")?.as_str()
}

fn image_alignment(node: &Value) -> Option<ImageAlignment> {
    let class = node
        .get("attrs")?
        .get("wrapperAttributes")?
        .get("class")?
        .as_str()?;

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
