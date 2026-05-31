mod text;
mod wiki_component;
mod include;
pub mod rgba_to_hex;

use serde_json::Value;

use crate::interpreter::{
    include::interpret_include,
    text::interpret_text,
    wiki_component::interpret_wiki_component,
};

pub fn interpret(json: &str) -> Result<String, String> {
    let value: Value = serde_json::from_str(json).map_err(|error| error.to_string())?;
    let content = value
        .get("content")
        .and_then(Value::as_array)
        .ok_or_else(|| "interpreter expected doc.content array".to_string())?;

    let mut output = String::new();

    for (index, node) in content.iter().enumerate() {
        let debug_line = identify_node(index + 1, node)?;
        println!("{}", debug_line);
        output.push_str(&debug_line);
        output.push('\n');
    }

    Ok(output)
}

fn identify_node(index: usize, node: &Value) -> Result<String, String> {
    match node.get("type").and_then(Value::as_str) {
        Some("Include") => interpret_include(index, node),
        Some("tabView") | Some("Collapsible") | Some("Note") => {
            interpret_wiki_component(index, node)
        }
        Some(_) => interpret_text(index, node),
        None => Err(format!("interpreter expected node type at doc.content[{index}]")),
    }
}
