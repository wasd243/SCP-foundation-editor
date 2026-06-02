use serde_json::Value;

use crate::interpreter::utils::get_marks::get_marks_by_type;

pub(super) fn interpret_size_text(node: &Value, output: String) -> Result<String, String> {
    let Some(size) = size_mark(node) else {
        return Ok(output);
    };

    Ok(format!("[[size {size}]]{output}[[/size]]"))
}

fn size_mark(node: &Value) -> Option<&str> {
    get_marks_by_type(node, "Size")
        .into_iter()
        .find_map(|mark| mark.get("attrs")?.get("size")?.as_str())
}
