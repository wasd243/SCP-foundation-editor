use std::borrow::Cow;

use serde::Serialize;

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

    // Tokenize and parse
    let tokens = ftml::tokenize(&wikitext);
    let parsed_result = ftml::parse(&tokens, &page_info, &settings);

    // Convert to AST
    // This would be the place to output AST and .json
    let (tree, _warnings) = parsed_result.into();

    let ast_json = serde_json::to_string_pretty(&tree)
        .map_err(|err| err.to_string())?;

    // This is a debug output for the parsed AST
    println!("{:?}", ast_json);

    use ftml::render::Render;

    // Render to HTML
    let renderer = ftml::render::html::HtmlRender;
    let html_output = renderer.render(&tree, &page_info, &settings);

    // This is a debug output for the parsed HTML
    println!("{:?}", html_output);

    Ok(FtmlParseOutput {
        html: html_output.body.to_string(),
        ast_json,
    })
}