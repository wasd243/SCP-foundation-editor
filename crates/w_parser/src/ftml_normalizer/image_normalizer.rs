use kuchiki::parse_html;
use kuchiki::traits::*;
use kuchiki::NodeRef;

fn div_ancestor(node: &NodeRef) -> bool {
    node.ancestors().skip(1).any(|ancestor| {
        ancestor
            .as_element()
            .map(|el| el.name.local.as_ref() == "div")
            .unwrap_or(false)
    })
}

fn create_alignleft_wrapper() -> NodeRef {
    let doc = parse_html().one("<div class=\"image-container alignleft\"></div>");
    let wrapper = doc.select_first("div").unwrap().as_node().clone();
    wrapper.detach();
    wrapper
}

pub fn normalize_images(html: &str) -> String {
    let document = parse_html().one(html);

    let targets: Vec<NodeRef> = document
        .select("img")
        .unwrap()
        .filter_map(|img| {
            let node = img.as_node().clone();
            if div_ancestor(&node) {
                None
            } else {
                Some(node)
            }
        })
        .collect();

    for img in targets {
        let wrapper = create_alignleft_wrapper();
        img.insert_before(wrapper.clone());
        img.detach();
        wrapper.append(img);
    }

    let mut out = Vec::new();
    document.serialize(&mut out).unwrap();

    String::from_utf8(out).unwrap()
}
