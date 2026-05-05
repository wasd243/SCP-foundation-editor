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
        item: item.to_string(),
        clearance_raw: clearance_raw.to_string(),
        secondary_raw: secondary_raw.to_string(),
        container_raw: container_raw.to_string(),
        secondary_icon_raw: secondary_icon_raw.to_string(),
        disruption_raw: disruption_raw.to_string(),
        risk_raw: risk_raw.to_string(),
        anim_checked,
        shiver_checked,
    };

    let data = normalize_input(input);
    Ok(render_acs(&data))
}
