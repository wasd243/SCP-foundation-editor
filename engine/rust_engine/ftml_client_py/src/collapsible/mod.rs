mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::parse_collapsible_data;
use self::render::render_html;

pub fn process_collapsible(
    _py: Python<'_>,
    text: &str,
    store: &PyAny,
    inner_parser_cb: &PyAny,
    theme_type: &str,
) -> PyResult<String> {
    let re = Regex::new(r#"(?is)\[\[collapsible([^\]]*)\]\](.*?)\[\[/collapsible\]\]"#).unwrap();
    let mut output = String::with_capacity(text.len());
    let mut last_end = 0;

    for caps in re.captures_iter(text) {
        let mat = caps.get(0).unwrap();
        output.push_str(&text[last_end..mat.start()]);

        let source = mat.as_str();
        let Some(data) = parse_collapsible_data(source) else {
            output.push_str(source);
            last_end = mat.end();
            continue;
        };
        let inner_html: String = inner_parser_cb
            .call1((data.content.as_str(), theme_type))?
            .extract()?;
        let html = render_html(&data, &inner_html);
        let replacement: String = store
            .call_method1("register_html", (data.source.as_str(), "collapsible", html))?
            .extract()?;
        output.push_str(&replacement);

        last_end = mat.end();
    }

    output.push_str(&text[last_end..]);
    Ok(output)
}
