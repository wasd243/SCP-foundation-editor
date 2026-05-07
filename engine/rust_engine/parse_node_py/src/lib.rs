#![allow(unsafe_op_in_unsafe_fn)]
#![allow(clippy::too_many_arguments)] // 部分组件的参数就那样，不需要倒腾那种struct
#![allow(clippy::useless_conversion)] // pyO3已自动处理，无需手动

mod acs;
mod aim;

use pyo3::prelude::*;

#[pymodule]
fn parse_node_py(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(acs::parse_acs_component, m)?)?;
    m.add_function(wrap_pyfunction!(aim::parse_aim_component, m)?)?;
    Ok(())
}
