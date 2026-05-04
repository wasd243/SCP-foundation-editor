mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::parse_fakeprot_data;
use self::render::render_html;

pub fn process_fakeprot(
    _py: Python<'_>,
    text: &str,
    store: &PyAny,
    inner_parser_cb: &PyAny,
    theme_type: &str,
) -> PyResult<String> {
    let mut result = Vec::new();
    let mut cursor = 0;
    let start_re = Regex::new(r#"(?i)\[\[div\s+class=["']fakeprot["']\]\]"#).unwrap();

    loop {
        let Some(start_match) = start_re.find(&text[cursor..]) else {
            result.push(text[cursor..].to_string());
            break;
        };
        let div_start = cursor + start_match.start();

        let Some(data) = parse_fakeprot_data(text, div_start) else {
            result.push(text[cursor..div_start + 5].to_string());
            cursor = div_start + 5;
            continue;
        };

        let parsed_coll: String = inner_parser_cb
            .call1((data.collapsible_content.trim(), theme_type))?
            .extract()?;
        let ll_html = render_html(&data, &parsed_coll);
        let replacement: String = store
            .call_method1("register_html", (data.source.as_str(), "login-logout", ll_html))?
            .extract()?;

        result.push(text[cursor..div_start].to_string());
        result.push(replacement);
        cursor = data.end_pos;
    }

    Ok(result.join(""))
}
