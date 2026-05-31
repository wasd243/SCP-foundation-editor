use serde_json::Value;

use crate::interpreter::rgba_to_hex::color_to_wikidot_hex;

pub fn interpret_color_text(node: &Value, output: String) -> Result<String, String> {
    let Some(color) = color_text_mark(node) else {
        return Ok(output);
    };

    let color = color_to_wikidot_hex(color)?;
    Ok(format!("###{color}|{output}##"))
}

fn color_text_mark(node: &Value) -> Option<&str> {
    node.get("marks")?
        .as_array()?
        .iter()
        .find(|mark| mark.get("type").and_then(Value::as_str) == Some("ColorText"))?
        .get("color")?
        .as_str()
}
