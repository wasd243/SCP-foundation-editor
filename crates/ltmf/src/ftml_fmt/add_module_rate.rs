use regex::Regex;
use std::fs;

const MODULE_RATE_STATUS: &str = concat!(
    env!("CARGO_MANIFEST_DIR"),
    "/../../temp/module_rate_status.txt"
);

/// Prepend the `[[module rate]]` Wikitext block (built from the module-rate
/// status file) to the editor content.
pub(super) fn add_module_rate(ftml: &str) -> Result<String, String> {
    let status = fs::read_to_string(MODULE_RATE_STATUS).map_err(|e| e.to_string())?;
    let module_rate = build_module_rate(&status);

    // MODULE_RATE=FALSE yields an empty block; leave the content untouched.
    if module_rate.is_empty() {
        return Ok(ftml.to_string());
    }

    Ok(format!("{module_rate}\n{ftml}"))
}

/// Render the module-rate block from a status string of the form
/// `MODULE_RATE=TRUE|FALSE\nALIGNMENTS=LEFT|RIGHT|CENTER|NONE`.
fn build_module_rate(status: &str) -> String {
    // Rule 1: MODULE_RATE=FALSE (or absent) exports nothing.
    if !is_module_rate_on(status) {
        return String::new();
    }

    // Rule 2: MODULE_RATE=TRUE wraps `[[module rate]]` in its alignment block.
    match alignment(status).as_str() {
        "LEFT" => "[[<]]\n[[module rate]]\n[[/<]]".to_string(),
        "RIGHT" => "[[>]]\n[[module rate]]\n[[/>]]".to_string(),
        "CENTER" => "[[=]]\n[[module rate]]\n[[/=]]".to_string(),
        // NONE and any unrecognized value: bare module rate.
        _ => "[[module rate]]".to_string(),
    }
}

fn is_module_rate_on(status: &str) -> bool {
    Regex::new(r"MODULE_RATE=(\w+)")
        .unwrap()
        .captures(status)
        .is_some_and(|c| c[1].eq_ignore_ascii_case("TRUE"))
}

fn alignment(status: &str) -> String {
    Regex::new(r"ALIGNMENTS=(\w+)")
        .unwrap()
        .captures(status)
        .map(|c| c[1].to_uppercase())
        .unwrap_or_else(|| "NONE".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn module_rate_false_returns_empty() {
        assert_eq!(build_module_rate("MODULE_RATE=FALSE\nALIGNMENTS=NONE"), "");
        // Alignment is irrelevant when the module is off.
        assert_eq!(build_module_rate("MODULE_RATE=FALSE\nALIGNMENTS=LEFT"), "");
    }

    #[test]
    fn module_rate_true_none_is_bare() {
        assert_eq!(
            build_module_rate("MODULE_RATE=TRUE\nALIGNMENTS=NONE"),
            "[[module rate]]"
        );
    }

    #[test]
    fn module_rate_true_left() {
        assert_eq!(
            build_module_rate("MODULE_RATE=TRUE\nALIGNMENTS=LEFT"),
            "[[<]]\n[[module rate]]\n[[/<]]"
        );
    }

    #[test]
    fn module_rate_true_right() {
        assert_eq!(
            build_module_rate("MODULE_RATE=TRUE\nALIGNMENTS=RIGHT"),
            "[[>]]\n[[module rate]]\n[[/>]]"
        );
    }

    #[test]
    fn module_rate_true_center() {
        assert_eq!(
            build_module_rate("MODULE_RATE=TRUE\nALIGNMENTS=CENTER"),
            "[[=]]\n[[module rate]]\n[[/=]]"
        );
    }
}
