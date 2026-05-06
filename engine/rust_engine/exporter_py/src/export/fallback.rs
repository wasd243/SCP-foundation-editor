use crate::export::context::{build_top_modules, snapshot_bool};
use crate::export::wikidot_post::{cleanup_body, finalize_output};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};

pub fn export_with_fallback(
    py: Python<'_>,
    html: &str,
    snapshot: &Bound<'_, PyDict>,
) -> PyResult<String> {
    let bs4 = py.import_bound("bs4")?;
    let soup = bs4
        .getattr("BeautifulSoup")?
        .call1((html, "html.parser"))?;

    let root_kwargs = PyDict::new_bound(py);
    root_kwargs.set_item("id", "editor-root")?;
    let root = soup.call_method("find", (), Some(&root_kwargs))?;
    if root.is_none() {
        return Ok(String::new());
    }

    let parse_node = py
        .import_bound("formats.wikidot.parse_node.parse_node")?
        .getattr("handle_parse_node")?;
    let parse_state = PyDict::new_bound(py);
    parse_state.set_item("better_footnotes", snapshot_bool(snapshot, "bf_on", false))?;
    parse_state.set_item(
        "mono_security",
        snapshot_bool(snapshot, "mono_security_on", true),
    )?;
    parse_state.set_item(
        "line_break_symbol_lock",
        snapshot_bool(snapshot, "line_break_symbol_lock_on", false),
    )?;

    let contents = root.getattr("contents")?;
    let mut body = String::new();
    for item in contents.iter()? {
        let node: Bound<'_, PyAny> = match item {
            Ok(v) => v,
            Err(_) => continue,
        };
        let parsed = parse_node
            .call1((node.clone(), parse_state.clone()))
            .and_then(|x| x.extract::<String>())
            .unwrap_or_else(|_| {
                node.call_method0("get_text")
                    .and_then(|x| x.extract::<String>())
                    .unwrap_or_default()
            });
        body.push_str(&parsed);
    }

    let mut top = build_top_modules(
        snapshot,
        false,
        false,
        "",
        html.contains("data-toc-anchor"),
    );
    top.push_str(&cleanup_body(&body));
    Ok(finalize_output(String::new(), top, "", snapshot))
}
