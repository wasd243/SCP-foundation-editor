use crate::export::ast::ExportTree;

pub mod wikitext;

pub trait Render {
    type Output;

    fn render(&self, tree: &ExportTree) -> Self::Output;
}
