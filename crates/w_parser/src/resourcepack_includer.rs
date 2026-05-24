use ftml::includes::{FetchedPage, IncludeRef, Includer};
use ftml::data::PageRef;

use std::borrow::Cow;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug)]
pub struct ResourcepackIncluder {
    root: PathBuf,
}

impl ResourcepackIncluder {
    pub fn new(root: impl Into<PathBuf>) -> Self {
        Self { root: root.into() }
    }

    fn include_path(&self, include: &IncludeRef<'_>) -> PathBuf {
        // Example page_ref display:
        // component:image-block
        //
        // Convert to:
        // resourcepack/includes/component/image-block.ftml

        let page_ref = include.page_ref().to_string();

        let safe_path = page_ref
            .replace([':', '\\'], "/")
            .trim_start_matches('/')
            .to_string();

        self.root
            .join("includes")
            .join(format!("{safe_path}.ftml"))
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

            let content = self
                .read_include_file(&path)
                .map(Cow::Owned);

            pages.push(FetchedPage {
                page_ref,
                content,
            });
        }

        Ok(pages)
    }

    fn no_such_include(
        &mut self,
        page_ref: &PageRef,
    ) -> Result<Cow<'t, str>, Self::Error> {
        Ok(Cow::Owned(format!(
            "[[include-missing {page_ref}]]"
        )))
    }
}
