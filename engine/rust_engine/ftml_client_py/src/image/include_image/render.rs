use super::model::IncludeImageData;

fn normalize_dimension(value: &str) -> String {
    let value = value.trim();
    if value.is_empty() {
        return "auto".to_string();
    }
    if value.ends_with("px") || value.ends_with('%') {
        value.to_lowercase()
    } else {
        format!("{value}px")
    }
}

pub fn render_html(data: &IncludeImageData) -> String {
    let width = if data.width.is_empty() {
        "auto".to_string()
    } else {
        normalize_dimension(&data.width)
    };
    let height = if data.height.is_empty() {
        "auto".to_string()
    } else {
        normalize_dimension(&data.height)
    };
    let align = if data.align.is_empty() {
        "right"
    } else {
        data.align.as_str()
    };

    let mut img_style = String::from("max-width:100%; display:block; margin:0 auto 5px auto;");
    img_style.push_str(&format!(" width:{};", width));
    img_style.push_str(&format!(" height:{};", height));
    if align == "center" {
        img_style.push_str(" width:100% !important;");
    }

    let dim_html = format!(
        r#"<div style="background:#fff; padding:5px; border-bottom:1px solid #eee; font-size:0.9em; display:flex; flex-direction:column; gap:5px;"><div style="display:flex; align-items:center;"><b style="flex-shrink:0;">源: &nbsp;</b><span data-field="name" style="display:none;">{name}</span><span class="img-link-label" onclick="editImgLink(this)" onmousedown="event.stopPropagation();" style="color:blue; text-decoration:underline; cursor:pointer;">链接</span></div><div style="display:flex; justify-content:space-between; align-items:baseline;"><span><b>宽:</b> <span data-field="width" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{width_raw}</span></span> <span><b>高:</b> <span data-field="height" contenteditable="true" oninput="refreshImg(this)" onmousedown="event.stopPropagation();" style="min-width:30px; display:inline-block; border-bottom:1px dashed #ccc;">{height_raw}</span></span></div></div>"#,
        name = data.name,
        width_raw = if data.width.is_empty() { "auto" } else { data.width.as_str() },
        height_raw = if data.height.is_empty() { "auto" } else { data.height.as_str() },
    );

    format!(
        r#"<div class="scp-component image-block-box" data-type="image-block-adv" data-align="{align}" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" contenteditable="false"><button class="img-toggle-btn" onclick="toggleImgControls(this)" title="切换显示/隐藏控制栏" onmousedown="event.stopPropagation();">👁️</button><div class="img-controls-wrapper"><div class="img-align-controls"><button class="img-align-btn" onclick="setImgAlign(this, 'left')" onmousedown="event.stopPropagation();">靠左</button><button class="img-align-btn" onclick="setImgAlign(this, 'center')" onmousedown="event.stopPropagation();">置中</button><button class="img-align-btn" onclick="setImgAlign(this, 'right')" onmousedown="event.stopPropagation();">靠右</button></div>{dim_html}</div><div class="image-block-content"><img src="{name}" class="img-preview" style="{img_style}"><div class="img-placeholder" style="margin-bottom:5px;color:#888;text-align:center;display:none;">[图片预览]</div></div><div class="image-block-caption"><b>描述:</b> <span data-field="caption" contenteditable="true" onmousedown="event.stopPropagation();">{caption}</span></div></div>"#,
        align = align,
        name = data.name,
        img_style = img_style,
        dim_html = dim_html,
        caption = data.caption,
    )
}
