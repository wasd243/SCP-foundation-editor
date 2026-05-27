use kuchiki::parse_html;
use kuchiki::traits::*;

const DEFAULT_IMAGE_BLOCK_ALIGN_CLASS: &str = "block-right";

fn is_template_align_class(class_name: &str) -> bool {
    let lower = class_name.to_ascii_lowercase();

    lower == "block-{$align}" || lower == "block-{$align:}"
}

fn normalize_image_block_class(class_name: &str) -> String {
    let mut classes: Vec<&str> = class_name
        .split_whitespace()
        .filter(|class_name| !is_template_align_class(class_name))
        .collect();

    if !classes.iter().any(|class_name| {
        matches!(*class_name, "block-left" | "block-right" | "block-center")
    }) {
        classes.push(DEFAULT_IMAGE_BLOCK_ALIGN_CLASS);
    }

    classes.join(" ")
}

pub fn normalize_component_images(html: &str) -> String {
    let document = parse_html().one(html);

    if let Ok(nodes) = document.select(".scp-image-block") {
        for node in nodes {
            let mut attributes = node.attributes.borrow_mut();
            let class_name = attributes.get("class").unwrap_or("");
            let normalized = normalize_image_block_class(class_name);

            attributes.insert("class", normalized);
        }
    }

    let mut out = Vec::new();
    document.serialize(&mut out).unwrap();

    String::from_utf8(out).unwrap()
}
