#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NodeSource {
    ParseNode,
    FallbackText,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BodyNodeKind {
    Block { tag: String },
    Inline { tag: String },
    Text,
    Unknown,
}

#[derive(Debug, Clone)]
pub struct BodyNode {
    pub kind: BodyNodeKind,
    pub source: NodeSource,
    pub wikidot: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TopModuleKind {
    Theme,
    Rate,
    BetterFootnotes,
    Toc,
}

#[derive(Debug, Clone)]
pub struct TopModuleNode {
    pub kind: TopModuleKind,
    pub wikidot: String,
}

#[derive(Debug, Clone)]
pub struct StyleNode {
    pub wikidot: String,
}

#[derive(Debug, Clone)]
pub struct LicenseNode {
    pub wikidot: String,
}

#[derive(Debug, Clone, Default)]
pub struct ExportTree {
    pub has_root: bool,
    pub head_styles: Vec<StyleNode>,
    pub top_modules: Vec<TopModuleNode>,
    pub body_nodes: Vec<BodyNode>,
    pub license_blocks: Vec<LicenseNode>,
    pub mono_security: bool,
    pub has_email_example: bool,
}

impl ExportTree {
    pub fn push_style(&mut self, wikidot: String) {
        self.head_styles.push(StyleNode { wikidot });
    }

    pub fn push_top_module(&mut self, kind: TopModuleKind, wikidot: String) {
        self.top_modules.push(TopModuleNode { kind, wikidot });
    }

    pub fn push_body(&mut self, kind: BodyNodeKind, source: NodeSource, wikidot: String) {
        self.body_nodes.push(BodyNode {
            kind,
            source,
            wikidot,
        });
    }

    pub fn push_license(&mut self, wikidot: String) {
        self.license_blocks.push(LicenseNode { wikidot });
    }

    pub fn body_text(&self) -> String {
        let mut out = String::new();
        for node in &self.body_nodes {
            out.push_str(&node.wikidot);
        }
        out
    }

    pub fn last_body_ends_with_newline(&self) -> bool {
        self.body_nodes
            .last()
            .map(|n| n.wikidot.ends_with('\n'))
            .unwrap_or(true)
    }

    pub fn top_text(&self) -> String {
        let mut out = String::new();
        for node in &self.top_modules {
            out.push_str(&node.wikidot);
        }
        out
    }

    pub fn styles_text(&self) -> String {
        let mut out = String::new();
        for node in &self.head_styles {
            out.push_str(&node.wikidot);
        }
        out
    }

    pub fn license_text(&self) -> String {
        let mut out = String::new();
        for node in &self.license_blocks {
            out.push_str(&node.wikidot);
        }
        out
    }
}
