use pyo3::prelude::*;
use pyo3::types::PyDict;

pub fn snapshot_bool(snapshot: &Bound<'_, PyDict>, key: &str, default: bool) -> bool {
    snapshot
        .get_item(key)
        .ok()
        .flatten()
        .and_then(|v| v.extract::<bool>().ok())
        .unwrap_or(default)
}

pub fn build_theme_and_rate(
    snapshot: &Bound<'_, PyDict>,
    has_rate_box: bool,
    rate_hidden: bool,
    rate_align: &str,
    has_toc_anchor: bool,
) -> String {
    let mut rate_code = String::new();
    if has_rate_box && !rate_hidden {
        rate_code = match rate_align {
            "left" => "[[<]]\n[[module Rate]]\n[[/<]]\n".to_string(),
            "right" => "[[>]]\n[[module Rate]]\n[[/>]]\n".to_string(),
            _ => "[[module Rate]]\n".to_string(),
        };
    }

    let mut theme_code = String::new();
    if snapshot_bool(snapshot, "basalt_on", false) {
        let mut opts = Vec::new();
        if snapshot_bool(snapshot, "basalt_dark", false) {
            opts.push("darkmode=a");
        }
        if snapshot_bool(snapshot, "basalt_wide", false) {
            opts.push("wide=a");
        }
        if snapshot_bool(snapshot, "basalt_hide", false) {
            opts.push("hidetitle=a");
        }
        if opts.is_empty() {
            theme_code.push_str("[[include :scp-wiki-cn:theme:basalt]]\n");
        } else {
            theme_code.push_str(&format!(
                "[[include :scp-wiki-cn:theme:basalt 版式设置|{}]]\n",
                opts.join("|")
            ));
        }
    } else if snapshot_bool(snapshot, "shiver_on", false) {
        let suffix = if snapshot_bool(snapshot, "shiv_mo", false) {
            " mo=*"
        } else if snapshot_bool(snapshot, "shiv_kl", false) {
            " kl=*"
        } else if snapshot_bool(snapshot, "shiv_dub", false) {
            " dub=*"
        } else if snapshot_bool(snapshot, "shiv_ct", false) {
            " ct=*"
        } else if snapshot_bool(snapshot, "shiv_ba", false) {
            " ba=*"
        } else {
            ""
        };
        theme_code.push_str(&format!(
            "[[include :scp-wiki-cn:theme:shivering-night{}]]\n",
            suffix
        ));
    } else if snapshot_bool(snapshot, "bhl_on", false) {
        theme_code.push_str("[[include :scp-wiki-cn:theme:black-highlighter-theme]]\n");
        if snapshot_bool(snapshot, "bhl_sidebar", false) {
            theme_code.push_str("[[include :scp-wiki:component:bhl-dark-sidebar]]\n");
        }
        if snapshot_bool(snapshot, "bhl_coll", false) {
            theme_code.push_str("[[include :scp-wiki:component:collapsible-sidebar]]\n");
        }
        if snapshot_bool(snapshot, "bhl_toggle", false) {
            theme_code.push_str("[[include :scp-wiki:component:toggle-sidebar-bhl]]\n");
        }
        if snapshot_bool(snapshot, "bhl_center", false) {
            theme_code.push_str("[[include :scp-wiki:component:centered-header-bhl]]\n");
        }
        if snapshot_bool(snapshot, "bhl_office", false) {
            theme_code.push_str("[[include :scp-wiki-cn:theme:scp-offices-theme]]\n");
        }
    }

    let mut final_code = format!("{}{}", theme_code, rate_code);
    if snapshot_bool(snapshot, "bf_on", false) {
        final_code.push_str("[[include :scp-wiki-cn:component:betterfootnotes]]\n");
    }
    if has_toc_anchor && !final_code.contains("[[toc]]") {
        final_code.push_str("[[toc]]\n");
    }

    final_code
}

pub fn email_css_block() -> &'static str {
    "[[module CSS]]\n\
.email-example .collapsible-block-folded a.collapsible-block-link {\n\
    animation: blink 0.8s ease-in-out infinite alternate;\n\
}\n\
@keyframes blink {\n\
    0% { color: transparent; }\n\
    50%, 100% { color: #b01; }\n\
}\n\
.email {border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.5)}\n\
.email-example a.collapsible-block-link {font-weight: bold;}\n\
.tofrom {margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon}\n\
[[/module]]\n"
}
