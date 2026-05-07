use crate::export::ast::{BodyNodeKind, ExportTree, NodeSource};
use crate::export::render::Render;

mod postprocess;

#[derive(Debug, Default)]
pub struct WikitextRender;

impl Render for WikitextRender {
    type Output = String;

    fn render(&self, tree: &ExportTree) -> String {
        if !tree.has_root {
            return String::new();
        }

        let mut head_styles = tree.styles_text();
        if tree.has_email_example && !head_styles.contains(email_css_block().trim()) {
            head_styles.push_str(email_css_block());
        }

        let mut final_code = tree.top_text();
        final_code.push_str(&postprocess::cleanup_body(&render_body_nodes(tree)));
        final_code.push_str(&tree.license_text());

        if tree.mono_security {
            final_code = postprocess::remove_mono_chinese_braces(&final_code);
        }

        let mut combined = format!("{}{}", head_styles, final_code);
        combined = postprocess::dedup_css_modules(&combined);
        postprocess::compress_newlines(combined.trim())
    }
}

fn render_body_nodes(tree: &ExportTree) -> String {
    let mut out = String::new();
    for node in &tree.body_nodes {
        if node.wikidot.trim().is_empty() {
            continue;
        }

        match (&node.kind, node.source) {
            (BodyNodeKind::Unknown, NodeSource::FallbackText)
            | (BodyNodeKind::Block { .. }, NodeSource::FallbackText) => {
                if !out.ends_with('\n') {
                    out.push('\n');
                }
                out.push_str(&node.wikidot);
                if !out.ends_with('\n') {
                    out.push('\n');
                }
            }
            _ => out.push_str(&node.wikidot),
        }
    }
    out
}

fn email_css_block() -> &'static str {
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
