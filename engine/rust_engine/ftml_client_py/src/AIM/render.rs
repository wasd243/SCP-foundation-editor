use super::parse::AimData;

pub fn render_html(data: &AimData) -> String {
    format!(
        r#"<div class="scp-component aim-box" data-type="aim" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-blocks="{blocks_arg}" contenteditable="false"><table class="aim-table"><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">&#39033;&#30446;&#32534;&#21495;</div><div class="aim-value aim-header-title" data-field="xxxx" contenteditable="true">{XXXX}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">&#31561;&#32423; / &#20844;&#24320;</div><div class="aim-value" data-field="lv" contenteditable="true">{lv}</div></td></tr><tr style="{row_style_top}"><td colspan="2"><div class="aim-label">&#25910;&#23481;&#31561;&#32423;</div><div class="aim-value" data-field="cc" contenteditable="true">{cc}</div></td><td colspan="2" style="text-align: right;"><div class="aim-label">&#25200;&#21160;&#31561;&#32423;</div><div class="aim-value" data-field="dc" contenteditable="true">{dc}</div></td></tr><tr style="{row_style_bottom} text-align: center; background: #fafafa;"><td><div class="aim-label">&#36127;&#36131;&#31449;&#28857;</div><div class="aim-value" data-field="site" contenteditable="true">{site}</div></td><td><div class="aim-label">&#31449;&#28857;&#20027;&#31649;</div><div class="aim-value" data-field="dir" contenteditable="true">{dir}</div></td><td><div class="aim-label">&#39318;&#24109;&#30740;&#31350;&#21592;</div><div class="aim-value" data-field="head" contenteditable="true">{head}</div></td><td><div class="aim-label">&#25351;&#27966;&#29305;&#36963;&#38431;</div><div class="aim-value" data-field="mtf" contenteditable="true">{mtf}</div></td></tr></table><div class="aim-footer">AIM Module</div></div>"#,
        blocks_arg = data.blocks_arg,
        row_style_top = data.row_style_top,
        row_style_bottom = data.row_style_bottom,
        XXXX = data.XXXX,
        lv = data.lv,
        cc = data.cc,
        dc = data.dc,
        site = data.site,
        dir = data.dir,
        head = data.head,
        mtf = data.mtf,
    )
}
