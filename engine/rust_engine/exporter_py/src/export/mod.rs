use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::panic::{catch_unwind, AssertUnwindSafe};

mod ast;
mod pipeline;
mod render;

use self::render::Render;
use self::render::wikitext::WikitextRender;

#[pyfunction]
pub fn export_html_to_wikidot(
    py: Python<'_>,
    html: &str,
    snapshot: &Bound<'_, PyDict>,
) -> PyResult<String> {
    let primary = catch_unwind(AssertUnwindSafe(|| {
        let tree = pipeline::build_export_tree(py, html, snapshot)?;
        Ok::<String, PyErr>(WikitextRender.render(&tree))
    }));
    match primary {
        Ok(Ok(code)) => Ok(code),
        Ok(Err(_)) | Err(_) => {
            let secondary = catch_unwind(AssertUnwindSafe(|| {
                let tree = pipeline::build_fallback_tree(py, html, snapshot)?;
                Ok::<String, PyErr>(WikitextRender.render(&tree))
            }));
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
