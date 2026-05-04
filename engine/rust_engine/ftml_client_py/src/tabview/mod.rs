mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::parse_tabview_data;
use self::render::render_html;

pub fn process_tabview(
    text: &str,
    store: &PyAny,
    inner_parser_cb: &PyAny,
    theme_type: &str,
) -> PyResult<String> {
    let tabview_re = Regex::new(r#"(?is)\[\[tabview\]\](.*?)\[\[/tabview\]\]"#).unwrap();
    let mut result = String::with_capacity(text.len());
    let mut last_end = 0;

    for mat in tabview_re.find_iter(text) {
        result.push_str(&text[last_end..mat.start()]);

        let source = mat.as_str();
        let Some(data) = parse_tabview_data(source) else {
            result.push_str(source);
            last_end = mat.end();
            continue;
        };

        let mut inner_html = Vec::new();
        for tab in &data.tabs {
            let parsed: String = inner_parser_cb
                .call1((tab.body.as_str(), theme_type))?
                .extract()?;
            inner_html.push(parsed);
        }

        let html = render_html(&data, &inner_html);
        let replacement: String = store
            .call_method1("register_html", (source, "tabview", html))?
            .extract()?;
        result.push_str(&replacement);

        last_end = mat.end();
    }

    result.push_str(&text[last_end..]);
    Ok(result)
}
