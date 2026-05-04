mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::{parse_better_footnote, parse_standard_footnote};
use self::render::render_html;

fn replace_with_footnote(store: &PyAny, source: &str, html: String) -> PyResult<String> {
    store
        .call_method1("register_html", (source, "footnote", html))?
        .extract()
}

pub fn process_footnotes(text: &str, store: &PyAny) -> PyResult<String> {
    let standard_re = Regex::new(r#"(?is)\[\[footnote\]\](.*?)\[\[/footnote\]\]"#).unwrap();
    let better_re = Regex::new(
        r#"(?is)\[\[span\s+class=["']fnnum["']\]\](.*?)\[\[/span\]\]\[\[span\s+class=["']fncon["']\]\](.*?)\[\[/span\]\]"#,
    )
    .unwrap();

    let mut result = text.to_string();

    result = standard_re
        .replace_all(&result, |caps: &regex::Captures| {
            let source = caps.get(0).map(|m| m.as_str()).unwrap_or_default();
            let Some(data) = parse_standard_footnote(source) else {
                return source.to_string();
            };
            replace_with_footnote(store, &data.source, render_html(&data)).unwrap_or_else(|_| {
                source.to_string()
            })
        })
        .to_string();

    result = better_re
        .replace_all(&result, |caps: &regex::Captures| {
            let source = caps.get(0).map(|m| m.as_str()).unwrap_or_default();
            let Some(data) = parse_better_footnote(source) else {
                return source.to_string();
            };
            replace_with_footnote(store, &data.source, render_html(&data)).unwrap_or_else(|_| {
                source.to_string()
            })
        })
        .to_string();

    Ok(result)
}
