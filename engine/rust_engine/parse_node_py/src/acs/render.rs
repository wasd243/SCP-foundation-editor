use super::model::AcsData;

pub fn render_acs(data: &AcsData) -> String {
    let anim = if data.anim_checked {
        "[[include :scp-wiki-cn:component:acs-animation]]\n"
    } else {
        ""
    };

    let mut sec_line = String::new();
    if !data.secondary.is_empty() {
        sec_line.push_str(&format!("|secondary-class={}\n", data.secondary));
        if !data.secondary_icon.is_empty() {
            sec_line.push_str(&format!("|secondary-icon={}\n", data.secondary_icon));
        }
    }

    let mut res = format!(
        "[[include :scp-wiki-cn:component:anomaly-class-bar-source\n|lang=cn\n|item-number={}\n|clearance={}\n|container-class={}\n{}|disruption-class={}\n|risk-class={}\n]]",
        data.item, data.clearance, data.container, sec_line, data.disruption, data.risk
    );

    if data.shiver_checked {
        res = format!("[[div class=\"Shivering-ACS\"]]\n{}\n[[/div]]", res);
    }

    format!("\n{}{}\n", anim, res)
}
