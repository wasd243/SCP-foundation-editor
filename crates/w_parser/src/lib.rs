//! w_parser is the main wikidot -> HTML parser based on ftml

use std::borrow::Cow;
use serde::Serialize;

use crate::ftml_interceptor::module_rate::rate_interceptor::rate_interceptor;
use crate::ftml_interceptor::note::note_interceptor::note_interceptor;
use crate::ftml_interceptor::note::note_parser::note_parser;
use crate::ftml_interceptor::note::note_cleaner::note_cleaner;

mod ftml_interceptor;

#[derive(Serialize)]
pub struct FtmlParseOutput {
    pub html: String,
    pub ast_json: String,
}

pub fn render_wikidot_to_html_and_ast(source_text: &str) -> Result<FtmlParseOutput, String> {
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

    // Intercept unsupported Wikidot runtime blocks before FTML tokenization.
    // Module rate will be intercepted because ftml is not supported yet.
    wikitext = rate_interceptor(&wikitext);
    // Note blocks are not supported yet, so they are intercepted here.
    // Intercept first, then parse after ftml output HTML.
    wikitext = note_interceptor(&wikitext);

    // Tokenize and parse
    let tokens = ftml::tokenize(&wikitext);
    let parsed_result = ftml::parse(&tokens, &page_info, &settings);

    // Convert to AST
    // This would be the place to output AST and .json
    let (tree, _warnings) = parsed_result.into();

    let ast_json = serde_json::to_string_pretty(&tree)
        .map_err(|err| err.to_string())?;

    use ftml::render::Render;

    // Render to HTML
    let renderer = ftml::render::html::HtmlRender;
    let mut html_output = renderer.render(&tree, &page_info, &settings);

    html_output.body = note_parser(&html_output.body);
    html_output.body = note_cleaner(&html_output.body);

    // This is a debug output for the parsed HTML
    println!("{:?}", html_output);

    Ok(FtmlParseOutput {
        html: html_output.body.to_string(),
        ast_json,
    })
}
