use html_escape::encode_text;

use super::model::{AcsData, AcsInput};

pub fn normalize_input(input: AcsInput) -> AcsData {
    let secondary = lower_trim(&input.secondary_raw);
    let secondary = if secondary == "none" {
        String::new()
    } else {
        secondary
    };

    let container = if secondary.is_empty() {
        lower_trim(&input.container_raw)
    } else {
        "机密".to_string()
    };

    AcsData {
        item: escape(&input.item),
        clearance: extract_clearance(&input.clearance_raw),
        container: escape(&container),
        secondary: escape(&secondary),
        secondary_icon: escape(&input.secondary_icon_raw.trim()),
        disruption: escape(&lower_trim(&input.disruption_raw)),
        risk: escape(&lower_trim(&input.risk_raw)),
        anim_checked: input.anim_checked,
        shiver_checked: input.shiver_checked,
    }
}

fn extract_clearance(raw: &str) -> String {
    let mut digits = String::new();
    let mut started = false;

    for ch in raw.chars() {
        if ch.is_ascii_digit() {
            digits.push(ch);
            started = true;
        } else if started {
            break;
        }
    }

    if digits.is_empty() {
        "1".to_string()
    } else {
        digits
    }
}

fn lower_trim(value: &str) -> String {
    value.trim().to_lowercase()
}

fn escape(value: &str) -> String {
    encode_text(value).into_owned()
}
