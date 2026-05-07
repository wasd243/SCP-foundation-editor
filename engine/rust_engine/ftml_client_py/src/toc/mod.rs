mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::{parse_toc_heading, parse_toc_placeholder};
use self::render::{render_heading_marker_html, render_marker_html, render_placeholder_html};

pub fn process_toc(
    text: &str,
    store: &PyAny,
    _inner_parser_cb: &PyAny,
    _theme_type: &str,
) -> PyResult<String> {
    let toc_re = Regex::new(r"(?i)\[\[toc\]\]").unwrap();
    let heading_re = Regex::new(r#"(?m)(^|\n)(\+{1,6})\s*\[\[#\s*([^\]]+)\]\]\s*(.*)"#).unwrap();

    let mut result = replace_toc_placeholders(text, &toc_re, store)?;
    result = replace_toc_headings(&result, &heading_re, store)?;
    Ok(result)
}

fn replace_toc_placeholders(text: &str, re: &Regex, store: &PyAny) -> PyResult<String> {
    let mut result = String::with_capacity(text.len());
    let mut last_end = 0;

    for mat in re.find_iter(text) {
        result.push_str(&text[last_end..mat.start()]);
        let source = mat.as_str();
        let data = parse_toc_placeholder(source);
        let html = render_placeholder_html();
        let replacement: String = store
            .call_method1("register_html", (data.source.as_str(), "toc", html))?
            .extract()?;
        result.push_str(&replacement);
        last_end = mat.end();
    }

    result.push_str(&text[last_end..]);
    Ok(result)
}

fn replace_toc_headings(text: &str, re: &Regex, store: &PyAny) -> PyResult<String> {
    let mut result = String::with_capacity(text.len());
    let mut last_end = 0;

    for caps in re.captures_iter(text) {
        let mat = caps.get(0).unwrap();
        result.push_str(&text[last_end..mat.start()]);

        let prefix = caps.get(1).map(|m| m.as_str()).unwrap_or_default();
        let pluses = caps.get(2).map(|m| m.as_str()).unwrap_or_default();
        let anchor = caps.get(3).map(|m| m.as_str()).unwrap_or_default();
        let title = caps.get(4).map(|m| m.as_str()).unwrap_or_default();
        let data = parse_toc_heading(mat.as_str(), prefix, pluses, anchor, title);
        let marker_html = render_marker_html(&data);
        let marker_uuid: String = store
            .call_method1(
                "register_html",
                (data.source.as_str(), "toc-anchor-marker", marker_html),
            )?
            .extract()?;
        result.push_str(&render_heading_marker_html(&data, &marker_uuid));

        last_end = mat.end();
    }

    result.push_str(&text[last_end..]);
    Ok(result)
}
