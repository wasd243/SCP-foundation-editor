use ftml::data::PageRef;
use ftml::includes::{FetchedPage, IncludeRef, Includer};

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
        let page_ref = include.page_ref();
        let page = page_ref.page();
        let branch = self.branch_name(page_ref);
        let file_name = self.file_name(page);

        match branch {
            Some(branch) => self
                .root
                .join("includes")
                .join("branch")
                .join(branch)
                .join(format!("{file_name}.ftml")),
            None => self
                .root
                .join("includes")
                .join("component")
                .join(format!("{file_name}.ftml")),
        }
    }

    fn branch_name(&self, page_ref: &PageRef) -> Option<&'static str> {
        if matches!(page_ref.site(), Some("component")) {
            return None;
        }

        if let Some(site) = page_ref.site().and_then(Self::site_branch) {
            return Some(site);
        }

        Self::page_branch(page_ref.page())
    }

    fn site_branch(site: &str) -> Option<&'static str> {
        match site {
            "scp-wiki-cn" => Some("CN"),
            "scp-wiki" => Some("EN"),
            _ => None,
        }
    }

    fn page_branch(page: &str) -> Option<&'static str> {
        let prefix = page.split(':').next().unwrap_or(page);

        if prefix == "scp-wiki-cn" || prefix.starts_with("scp-wiki-cn-") {
            Some("CN")
        } else if prefix == "scp-wiki" || prefix.starts_with("scp-wiki-") {
            Some("EN")
        } else {
            None
        }
    }

    fn file_name(&self, page: &str) -> String {
        page.rsplit(':')
            .next()
            .unwrap_or(page)
            .replace(['/', '\\'], "")
            .trim_start_matches('.')
            .to_string()
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
        log::warn!(target: "[w_parser::ResourcepackIncluder]", "no_such_include: {page_ref}");

        Ok(Cow::Owned(format!("[[include-missing {page_ref}]]")))
    }
}
