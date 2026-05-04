mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use parse::{extract_acs_data, inject_shivering};
use render::render_html;

pub fn process_acs(_py: Python<'_>, text: &str, store: &PyAny) -> PyResult<String> {
    let processed_text = inject_shivering(text);
    let anim_checked = if processed_text.contains("component:acs-animation") {
        "checked"
    } else {
        ""
    };

    let include_re =
        Regex::new(r"(?s)\[\[include :scp-wiki-cn:component:anomaly-class-bar-source.*?\]\]")
            .unwrap();
    let mut result = String::with_capacity(processed_text.len());
    let mut last_end = 0;

    for mat in include_re.find_iter(&processed_text) {
        result.push_str(&processed_text[last_end..mat.start()]);

        let source = mat.as_str();
        let data = extract_acs_data(source);
        let html = render_html(&data, anim_checked);
        let replacement: String = store
            .call_method1("register_html", (source, "acs", html))?
            .extract()?;
        result.push_str(&replacement);

        last_end = mat.end();
    }

    result.push_str(&processed_text[last_end..]);

    let animation_re = Regex::new(r"\[\[include :scp-wiki-cn:component:acs-animation\]\]").unwrap();
    Ok(animation_re.replace_all(&result, "").to_string())
}
