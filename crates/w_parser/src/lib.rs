//! w_parser is the main wikidot -> HTML parser based on ftml

use serde::Serialize;
use std::borrow::Cow;
use std::path::PathBuf;

use crate::ftml_interceptor::module_rate::rate_interceptor::rate_interceptor;
use crate::ftml_interceptor::note::note_cleaner::note_cleaner;
use crate::ftml_interceptor::note::note_interceptor::note_interceptor;
use crate::ftml_interceptor::note::note_parser::note_parser;

use crate::ftml_interceptor::preprocess_interceptor::{
    unused_variable_interceptor::unused_variable_interceptor,
    unused_newline_interceptor::unused_newline_interceptor,
};

use crate::resourcepack_includer::ResourcepackIncluder;
use crate::ftml_normalizer::image_normalizer::normalize_images;

mod ftml_interceptor;
mod resourcepack_includer;
mod ftml_normalizer;

const DEFAULT_RESOURCEPACK_ROOT: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../resourcepack");

#[derive(Serialize)]
pub struct FtmlParseOutput {
    pub html: String,
    pub ast_json: String,
}

pub fn render_wikidot_to_html_with_resourcepack(
    source_text: &str,
    resourcepack_root: impl Into<PathBuf>,
) -> Result<FtmlParseOutput, String> {
    let settings = ftml::settings::WikitextSettings::from_mode(
        ftml::settings::WikitextMode::Page,
        ftml::layout::Layout::Wikidot,
    );

    let page_info = ftml::data::PageInfo {
        page: Cow::Borrowed("page"),
        category: None,
        site: Cow::Borrowed("scp-wiki"),
        title: Cow::Borrowed("Editor"),
        alt_title: None,
        score: ftml::data::ScoreValue::Integer(0),
        tags: vec![],
        language: Cow::Borrowed("cn"),
    };

    let mut wikitext = source_text.to_string();

    ftml::preprocess(&mut wikitext);

    // Includer
    let (mut wikitext, _included_pages) = ftml::include(
        &wikitext,
        &settings,
        ResourcepackIncluder::new(resourcepack_root),
        || {
            std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "resourcepack includer returned mismatched include results",
            )
        },
    )
    .map_err(|err| err.to_string())?;

    // Intercept unsupported Wikidot runtime blocks before FTML tokenization.
    // Module rate will be intercepted because ftml is not supported yet.
    wikitext = rate_interceptor(&wikitext);

    // Note blocks are not supported yet, so they are intercepted here.
    // Intercept first, then parse after ftml output HTML.
    wikitext = note_interceptor(&wikitext);

    // Include blocks:
    // Sometimes preprocessing leaves malformed wikitext after include expansion.
    // Then FTML tokenization receives incorrect content,
    // and the parser falls back to normal text parsing.
    wikitext = unused_variable_interceptor(&wikitext);
    wikitext = unused_newline_interceptor(&wikitext);

    // Tokenize and parse
    let tokens = ftml::tokenize(&wikitext);

    let parsed_result = ftml::parse(&tokens, &page_info, &settings);

    // Convert to AST
    // This would be the place to output AST and .json
    let (tree, _warnings) = parsed_result.into();

    let ast_json = serde_json::to_string_pretty(&tree).map_err(|err| err.to_string())?;

    use ftml::render::Render;

    // Render to HTML
    let renderer = ftml::render::html::HtmlRender;
    let mut html_output = renderer.render(&tree, &page_info, &settings);

    html_output.body = note_parser(&html_output.body);
    html_output.body = note_cleaner(&html_output.body);

    html_output.body = normalize_images(&html_output.body);

    // This is a debug output for the parsed HTML
    println!("{:#?}", html_output);

    Ok(FtmlParseOutput {
        html: html_output.body.to_string(),
        ast_json,
    })
}

// Final handler to tauri
pub fn render_wikidot_to_html(source_text: &str) -> Result<FtmlParseOutput, String> {
    render_wikidot_to_html_with_resourcepack(source_text, DEFAULT_RESOURCEPACK_ROOT)
}
