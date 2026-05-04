mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use parse::parse_aim_data;
use render::render_html;

pub fn process_aim(_py: Python<'_>, text: &str, store: &PyAny) -> PyResult<String> {
    let include_re = Regex::new(
        r"(?is)\[\[include :scp-wiki-cn:component:advanced-information-methodology.*?\]\]",
    )
    .unwrap();
    let mut result = String::with_capacity(text.len());
    let mut last_end = 0;

    for mat in include_re.find_iter(text) {
        result.push_str(&text[last_end..mat.start()]);

        let source = mat.as_str();
        let data = parse_aim_data(source);
        let html = render_html(&data);
        let replacement: String = store
            .call_method1("register_html", (source, "aim", html))?
            .extract()?;
        result.push_str(&replacement);

        last_end = mat.end();
    }

    result.push_str(&text[last_end..]);
    Ok(result)
}
