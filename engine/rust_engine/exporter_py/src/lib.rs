#![allow(unsafe_op_in_unsafe_fn)]
#![allow(clippy::useless_conversion)]

mod exporter;
mod postprocess;
mod theme;

use pyo3::prelude::*;

#[pymodule]
fn exporter_py(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(exporter::export_html_to_wikidot, m)?)?;
    Ok(())
}
