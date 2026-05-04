use super::model::{BasaltDivData, BasaltDivKind};

pub fn render_html(data: &BasaltDivData, parsed_inner: &str, kind: &BasaltDivKind) -> String {
    match kind {
        BasaltDivKind::Floatbox { right } => {
            let right_cls = if *right { " right" } else { "" };
            format!(
                r#"<div class="scp-component div-box basalt-div basalt-floatbox-box{right_cls}" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="false" onclick="toggleDiv(this)" title="点击折叠/展开">[[div class="{}"]]</div><div class="div-content" contenteditable="true">{parsed_inner}</div></div>"#,
                data.classes.join(" ")
            )
        }
        BasaltDivKind::Special {
            primary_class,
            box_class,
        } => {
            let mut box_classes = vec![
                "scp-component".to_string(),
                "div-box".to_string(),
                "basalt-div".to_string(),
                (*box_class).to_string(),
            ];

            if matches!(primary_class.as_str(), "document" | "darkdocument") {
                box_classes.push("basalt-doc-wrapper full-width".to_string());
            }
            if primary_class.ends_with("_memo") {
                box_classes.push("basalt-memo-box".to_string());
            }

            format!(
                r#"<div class="{box_cls_str}" data-type="div-block" contenteditable="false"><div class="div-header" contenteditable="false" onclick="toggleDiv(this)" title="点击折叠/展开">[[div class="{}"]]</div><div class="div-content" contenteditable="true">{parsed_inner}</div></div>"#,
                data.classes.join(" "),
                box_cls_str = box_classes.join(" ")
            )
        }
    }
}
