mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::{normalize_center_wrapper, parse_include_image};
use self::render::render_html;

pub fn process_image(text: &str, store: &PyAny) -> PyResult<String> {
    let processed_text = normalize_center_wrapper(text);
    let include_re = Regex::new(r#"(?is)\[\[include component:image-block.*?\]\]"#).unwrap();
    let mut result = String::with_capacity(processed_text.len());
    let mut last_end = 0;

    for mat in include_re.find_iter(&processed_text) {
        result.push_str(&processed_text[last_end..mat.start()]);

        let source = mat.as_str();
        let data = parse_include_image(source);
        let html = render_html(&data);
        let replacement: String = store
            .call_method1("register_html", (source, "image-block", html))?
            .extract()?;
        result.push_str(&replacement);

        last_end = mat.end();
    }

    result.push_str(&processed_text[last_end..]);
    Ok(result)
}
