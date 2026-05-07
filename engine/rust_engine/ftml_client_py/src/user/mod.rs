mod model;
mod parse;
mod render;

use pyo3::prelude::*;
use regex::Regex;

use self::parse::{parse_advanced_user, parse_basic_user};
use self::render::render_html;

pub fn process_user(text: &str, store: &PyAny) -> PyResult<String> {
    let basic_re = Regex::new(r#"(?i)\[\[user\s+([^\]]+)\]\]"#).unwrap();
    let adv_re = Regex::new(r#"(?i)\[\[\*user\s+([^\]]+)\]\]"#).unwrap();

    let mut result = text.to_string();

    result = replace_users(&result, &basic_re, store, |_, name| {
        parse_basic_user(name)
    })?;
    result = replace_users(&result, &adv_re, store, |_, name| {
        parse_advanced_user(name)
    })?;

    Ok(result)
}

fn replace_users<F>(
    text: &str,
    re: &Regex,
    store: &PyAny,
    parse: F,
) -> PyResult<String>
where
    F: Fn(&str, &str) -> model::UserData,
{
    let mut result = String::with_capacity(text.len());
    let mut last_end = 0;

    for caps in re.captures_iter(text) {
        let mat = caps.get(0).unwrap();
        result.push_str(&text[last_end..mat.start()]);

        let source = mat.as_str();
        let name = caps.get(1).map(|m| m.as_str()).unwrap_or_default();
        let data = parse(source, name);
        let html = render_html(&data);
        let replacement: String = store
            .call_method1("register_html", (source, "user", html))?
            .extract()?;
        result.push_str(&replacement);

        last_end = mat.end();
    }

    result.push_str(&text[last_end..]);
    Ok(result)
}
