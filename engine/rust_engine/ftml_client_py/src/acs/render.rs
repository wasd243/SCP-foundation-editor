use super::model::{AcsData, color_for};

pub fn render_html(data: &AcsData, anim_checked: &str) -> String {
    let color = color_for(&data.cnt);
    let shiver_checked = if data.is_shiver { "checked" } else { "" };
    let secondary = if data.sec.is_empty() {
        "none"
    } else {
        data.sec.as_str()
    };
    let data_shivering = if data.is_shiver { "true" } else { "false" };

    format!(
        r#"
        <div class="scp-component acs-box" data-type="acs" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-clearance="{clr}" data-container="{cnt}" data-secondary="{secondary}" data-disruption="{dsr}" data-risk="{rsk}" data-shivering="{data_shivering}" style="--acs-color: {color};" contenteditable="false"><div class="acs-header-row" contenteditable="false"><div class="acs-title">SCP-CN &#24322;&#24120;&#20998;&#32423;&#26639;</div><div class="acs-toggles"><div class="acs-anim-toggle"><span>&#21160;&#30011;:</span><label class="switch"><input type="checkbox" class="acs-anim-checkbox" {anim_checked}><span class="slider"></span></label></div><div class="acs-shiver-toggle"><span>&#22812;&#29705;&#29827;&#36866;&#37197;:</span><label class="switch"><input type="checkbox" class="acs-shiver-checkbox" {shiver_checked}><span class="slider"></span></label></div></div><div class="acs-item-num" contenteditable="true" data-field="item-number">{item}</div></div><div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 10px;"><div><small style="color:#888; font-size:9px; text-transform:uppercase;">&#35768;&#21487;&#31561;&#32423;</small><br><b data-field="clearance" contenteditable="true">{clr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">&#39033;&#30446;&#31561;&#32423;</small><br><b data-field="container" style="color:var(--acs-color)" contenteditable="true">{cnt}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">&#27425;&#35201;&#31561;&#32423;</small><br><b data-field="secondary" contenteditable="true">{secondary}</b><div style="font-size:0.8em; border-top:1px solid #ccc; margin-top:2px;">Icon: <span data-field="secondary-icon" contenteditable="true" style="min-width:20px; display:inline-block; word-break: break-all;">{sec_icon}</span></div></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">&#25200;&#21160;&#31561;&#32423;</small><br><b data-field="disruption" contenteditable="true">{dsr}</b></div><div><small style="color:#888; font-size:9px; text-transform:uppercase;">&#39118;&#38505;&#31561;&#32423;</small><br><b data-field="risk" contenteditable="true">{rsk}</b></div></div></div>
        "#,
        clr = data.clr,
        cnt = data.cnt,
        secondary = secondary,
        dsr = data.dsr,
        rsk = data.rsk,
        data_shivering = data_shivering,
        color = color,
        anim_checked = anim_checked,
        shiver_checked = shiver_checked,
        item = data.item,
        sec_icon = data.sec_icon,
    )
}
