mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::parse_license_data;
use self::render::render_html;

pub fn process_license(text: &str, store: &PyAny) -> PyResult<String> {
    let block_re = Regex::new(
        r"(?is)\[\[include :scp-wiki-cn:component:license-box.*?\]\].*?\[\[include :scp-wiki-cn:component:license-box-end.*?\]\]",
    )
    .unwrap();
    let cleanup_end_re =
        Regex::new(r"(?is)\[\[include :scp-wiki-cn:component:license-box-end.*?\]\]").unwrap();
    let cleanup_start_re =
        Regex::new(r"(?is)\[\[include :scp-wiki-cn:component:license-box.*?\]\]").unwrap();

    let mut result = String::with_capacity(text.len());
    let mut last_end = 0;

    for mat in block_re.find_iter(text) {
        result.push_str(&text[last_end..mat.start()]);
        let source = mat.as_str();
        let data = parse_license_data(source);
        let html = render_html(&data);
        let replacement: String = store
            .call_method1("register_html", (source, "license", html))?
            .extract()?;
        result.push_str(&replacement);
        last_end = mat.end();
    }

    result.push_str(&text[last_end..]);
    let result = cleanup_end_re.replace_all(&result, "").to_string();
    Ok(cleanup_start_re.replace_all(&result, "").to_string())
}
