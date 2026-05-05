use pyo3::prelude::*;

use super::model::AcsInput;
use super::parse::normalize_input;
use super::render::render_acs;

#[pyfunction]
pub fn parse_acs_component(
    item: &str,
    clearance_raw: &str,
    secondary_raw: &str,
    container_raw: &str,
    secondary_icon_raw: &str,
    disruption_raw: &str,
    risk_raw: &str,
    anim_checked: bool,
    shiver_checked: bool,
) -> PyResult<String> {
    let input = AcsInput {
        item: item.into(),
        clearance_raw: clearance_raw.into(),
        secondary_raw: secondary_raw.into(),
        container_raw: container_raw.into(),
        secondary_icon_raw: secondary_icon_raw.into(),
        disruption_raw: disruption_raw.into(),
        risk_raw: risk_raw.into(),
        anim_checked,
        shiver_checked,
    };

    let data = normalize_input(input);
    Ok(render_acs(&data))
}
