#![allow(non_snake_case)]
#![allow(unsafe_op_in_unsafe_fn)]

mod ACS;
mod AIM;

use pyo3::prelude::*;

#[pyfunction]
fn process_acs(py: Python<'_>, text: &str, store: &PyAny) -> PyResult<String> {
    ACS::process_acs(py, text, store)
}

#[pyfunction]
fn process_aim(py: Python<'_>, text: &str, store: &PyAny) -> PyResult<String> {
    AIM::process_aim(py, text, store)
}

#[pymodule]
fn ftml_client_py(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_acs, m)?)?;
    m.add_function(wrap_pyfunction!(process_aim, m)?)?;
    Ok(())
}
