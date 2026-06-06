use serde_json::Value;

use crate::interpret::utils::get_marks::get_marks_by_type;
use crate::interpret::utils::rgba_to_hex::color_to_wikidot_hex;

pub(super) fn interpret_color_text(node: &Value, output: String) -> Result<String, String> {
    let Some(color) = color_text_mark(node) else {
        return Ok(output);
    };

    let color = color_to_wikidot_hex(color)?;
    Ok(format!("###{color}|{output}##"))
}

fn color_text_mark(node: &Value) -> Option<&str> {
    get_marks_by_type(node, "ColorText")
        .into_iter()
        .find_map(|mark| mark.get("color").and_then(Value::as_str))
}
