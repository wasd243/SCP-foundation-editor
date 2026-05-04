#![allow(unsafe_op_in_unsafe_fn)]
mod acs;
mod aim;
mod themes_div;
mod collapsible;
mod fake_prot;
mod footnotes;

use pyo3::prelude::*;

#[pyfunction]
fn process_acs(py: Python<'_>, text: &str, store: &PyAny) -> PyResult<String> {
    acs::process_acs(py, text, store)
}

#[pyfunction]
fn process_aim(py: Python<'_>, text: &str, store: &PyAny) -> PyResult<String> {
    aim::process_aim(py, text, store)
}

#[pyfunction]
fn process_basalt_divs(
    py: Python<'_>,
    text: &str,
    store: &PyAny,
    inner_parser_cb: &PyAny,
    theme_type: &str,
) -> PyResult<String> {
    themes_div::basalt::process_basalt_divs(py, text, store, inner_parser_cb, theme_type)
}

#[pyfunction]
fn process_collapsible(
    py: Python<'_>,
    text: &str,
    store: &PyAny,
    inner_parser_cb: &PyAny,
    theme_type: &str,
) -> PyResult<String> {
    collapsible::process_collapsible(py, text, store, inner_parser_cb, theme_type)
}

#[pyfunction]
fn process_fakeprot(
    py: Python<'_>,
    text: &str,
    store: &PyAny,
    inner_parser_cb: &PyAny,
    theme_type: &str,
) -> PyResult<String> {
    fake_prot::process_fakeprot(py, text, store, inner_parser_cb, theme_type)
}

#[pyfunction]
fn process_footnotes(text: &str, store: &PyAny) -> PyResult<String> {
    footnotes::process_footnotes(text, store)
}

#[pymodule]
fn ftml_client_py(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_acs, m)?)?;
    m.add_function(wrap_pyfunction!(process_aim, m)?)?;
    m.add_function(wrap_pyfunction!(process_basalt_divs, m)?)?;
    m.add_function(wrap_pyfunction!(process_collapsible, m)?)?;
    m.add_function(wrap_pyfunction!(process_fakeprot, m)?)?;
    m.add_function(wrap_pyfunction!(process_footnotes, m)?)?;
    Ok(())
}
