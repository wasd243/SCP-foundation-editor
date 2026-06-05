mod include;
mod text;
pub mod utils;
mod wiki_component;

use serde_json::Value;
use std::fs;

use crate::interpreter::{
    include::interpret_include, text::interpret_text, wiki_component::interpret_wiki_component,
};

const OUTPUT_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/output.ftml");

pub fn interpret(json: &str) -> Result<String, String> {
    let value: Value = serde_json::from_str(json).map_err(|error| error.to_string())?;
    let content = value
        .get("content")
        .and_then(Value::as_array)
        .ok_or_else(|| "interpreter expected doc.content array".to_string())?;

    let mut output = String::new();

    for (index, node) in content.iter().enumerate() {
        let debug_line = identify_node(index + 1, node)?;
        output.push_str(&debug_line);
        output.push('\n');
    }

    fs::write(OUTPUT_PATH, &output).map_err(|error| error.to_string())?;

    Ok(output)
}

fn identify_node(index: usize, node: &Value) -> Result<String, String> {
    match node.get("type").and_then(Value::as_str) {
        Some("Include") => interpret_include(index, node),
        Some("tabView") | Some("Collapsible") | Some("Note") | Some("Footnote") => {
            interpret_wiki_component(index, node)
        }
        Some(_) => interpret_text(index, node),
        None => Err(format!(
            "interpreter expected node type at doc.content[{index}]"
        )),
    }
}
