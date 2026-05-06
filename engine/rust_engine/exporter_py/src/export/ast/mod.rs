#[derive(Debug, Clone)]
pub enum BodyNode {
    Text(String),
}

#[derive(Debug, Clone, Default)]
pub struct ExportTree {
    pub has_root: bool,
    pub head_styles: Vec<String>,
    pub top_modules: Vec<String>,
    pub body_nodes: Vec<BodyNode>,
    pub license_blocks: Vec<String>,
    pub mono_security: bool,
    pub has_email_example: bool,
}

impl ExportTree {
    pub fn push_body(&mut self, text: String) {
        self.body_nodes.push(BodyNode::Text(text));
    }

    pub fn body_text(&self) -> String {
        let mut out = String::new();
        for node in &self.body_nodes {
            match node {
                BodyNode::Text(text) => out.push_str(text),
            }
        }
        out
    }

    pub fn top_text(&self) -> String {
        self.top_modules.join("")
    }

    pub fn styles_text(&self) -> String {
        self.head_styles.join("")
    }

    pub fn license_text(&self) -> String {
        self.license_blocks.join("")
    }
}
