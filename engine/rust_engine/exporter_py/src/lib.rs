#![allow(unsafe_op_in_unsafe_fn)]
#![allow(clippy::useless_conversion)]

mod export;

use pyo3::prelude::*;

#[pymodule]
fn exporter_py(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(export::export_html_to_wikidot, m)?)?;
    Ok(())
}
