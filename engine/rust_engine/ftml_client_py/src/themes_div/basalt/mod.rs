mod model;
mod parse;
mod render;

use pyo3::prelude::*;

use self::parse::{classify, parse_basalt_div_data};
use self::render::render_html;

pub fn process_basalt_divs(
    _py: Python<'_>,
    text: &str,
    store: &PyAny,
    inner_parser_cb: &PyAny,
    theme_type: &str,
) -> PyResult<String> {
    let mut output = Vec::new();
    let mut cursor = 0;

    loop {
        let Some(start_offset) = text[cursor..].find("[[div") else {
            output.push(text[cursor..].to_string());
            break;
        };
        let start_idx = cursor + start_offset;

        let Some(data) = parse_basalt_div_data(text, start_idx) else {
            output.push(text[cursor..start_idx + 5].to_string());
            cursor = start_idx + 5;
            continue;
        };

        let Some(kind) = classify(&data.classes) else {
            output.push(text[cursor..start_idx + 5].to_string());
            cursor = start_idx + 5;
            continue;
        };

        let parsed_inner: String = inner_parser_cb
            .call1((data.inner_content.as_str(), theme_type))?
            .extract()?;
        let html_shell = render_html(&data, &parsed_inner, &kind);
        let replacement: String = store
            .call_method1("register_html", (data.source_div.as_str(), "div-block", html_shell))?
            .extract()?;

        output.push(text[cursor..start_idx].to_string());
        output.push(replacement);
        cursor = data.end_pos;
    }

    Ok(output.join(""))
}
