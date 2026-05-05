#![allow(unsafe_op_in_unsafe_fn)]

mod acs;

use pyo3::prelude::*;

#[pymodule]
fn parse_node_py(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(acs::parse_acs_component, m)?)?;
    Ok(())
}
