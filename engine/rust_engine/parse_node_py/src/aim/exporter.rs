use pyo3::prelude::*;

use crate::aim::string::from_fields;
use crate::aim::string::to_wikidot;


#[pyfunction]
pub fn parse_aim_component(
    blocks: &str,
    xxxx: &str,
    lv: &str,
    cc: &str,
    dc: &str,
    site: &str,
    dir: &str,
    head: &str,
    mtf: &str,
) -> PyResult<String> {
    let model = from_fields(blocks, xxxx, lv, cc, dc, site, dir, head, mtf);
    Ok(to_wikidot(&model))
}
