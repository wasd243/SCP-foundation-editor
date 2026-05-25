use ftml::data::PageRef;
use ftml::includes::{FetchedPage, IncludeRef, Includer};

use std::borrow::Cow;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug)]
pub struct ResourcepackIncluder {
    component_root: PathBuf,
}

impl ResourcepackIncluder {
    pub fn new(root: impl Into<PathBuf>) -> Self {
        Self {
            component_root: root.into().join("includes").join("component"),
        }
    }

    fn include_path(&self, include: &IncludeRef<'_>) -> PathBuf {
        // Example page_ref display:
        // component:image-block
        //
        // Convert to:
        // resourcepack/includes/component/image-block.ftml

        let page = include.page_ref().page();
        let file_name = page
            .rsplit(':')
            .next()
            .unwrap_or(page)
            .replace(['/', '\\'], "")
            .trim_start_matches('.')
            .to_string();

        self.component_root.join(format!("{file_name}.ftml"))
    }

    fn read_include_file(&self, path: &Path) -> Option<String> {
        fs::read_to_string(path).ok()
    }
}

impl<'t> Includer<'t> for ResourcepackIncluder {
    type Error = std::io::Error;

    fn include_pages(
        &mut self,
        includes: &[IncludeRef<'t>],
    ) -> Result<Vec<FetchedPage<'t>>, Self::Error> {
        let mut pages = Vec::new();

        for include in includes {
            let page_ref = include.page_ref().clone();
            let path = self.include_path(include);

            let content = self.read_include_file(&path).map(Cow::Owned);

            pages.push(FetchedPage { page_ref, content });
        }

        Ok(pages)
    }

    fn no_such_include(&mut self, page_ref: &PageRef) -> Result<Cow<'t, str>, Self::Error> {
        eprintln!("[w_parser::ResourcepackIncluder] no_such_include: {page_ref}");

        Ok(Cow::Owned(format!("[[include-missing {page_ref}]]")))
    }
}
