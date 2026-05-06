use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::panic::{catch_unwind, AssertUnwindSafe};

mod context;
mod fallback;
mod html_ast;
mod wikidot_post;

#[pyfunction]
pub fn export_html_to_wikidot(
    py: Python<'_>,
    html: &str,
    snapshot: &Bound<'_, PyDict>,
) -> PyResult<String> {
    let primary = catch_unwind(AssertUnwindSafe(|| html_ast::export_from_ast(py, html, snapshot)));
    match primary {
        Ok(Ok(code)) => Ok(code),
        Ok(Err(_)) | Err(_) => {
            let secondary =
                catch_unwind(AssertUnwindSafe(|| fallback::export_with_fallback(py, html, snapshot)));
            match secondary {
                Ok(Ok(code)) => Ok(code),
                Ok(Err(_)) => Ok(String::new()),
                Err(_) => Err(PyRuntimeError::new_err(
                    "exporter_py crashed during export and fallback",
                )),
            }
        }
    }
}
