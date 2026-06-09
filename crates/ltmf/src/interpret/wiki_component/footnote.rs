use serde_json::Value;

use crate::interpret::{
    text::interpret_text_content,
    utils::{get_intercepted_content::get_intercepted_content, get_types::has_type},
};

pub(super) fn interpret_footnote(node: &Value, output: String) -> Result<String, String> {
    if !has_type(node, "Footnote") {
        return Ok(output);
    }

    let output = get_intercepted_content(node, interpret_text_content);

    Ok(format!("[[footnote]]{output}[[/footnote]]"))
}
