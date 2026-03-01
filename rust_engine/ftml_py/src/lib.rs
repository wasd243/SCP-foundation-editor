use pyo3::prelude::*;
use std::borrow::Cow;

#[pyfunction]
fn render_wikidot_to_html(source_text: &str) -> PyResult<String> {
    // 1. 准备配置
    let settings = ftml::settings::WikitextSettings::from_mode(
        ftml::settings::WikitextMode::Page,
        ftml::layout::Layout::Wikidot,
    );

    // 2. 准备页面上下文
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

    // 3. 预处理
    let mut wikitext = source_text.to_string();
    ftml::preprocess(&mut wikitext);

    // 4. 词法分析
    let tokens = ftml::tokenize(&wikitext);

    // 5. 语法分析
    let parsed_result = ftml::parse(&tokens, &page_info, &settings);

    // 6. 解包 AST
    let (tree, _errors) = parsed_result.into();

    // 7. 渲染降维打击
    use ftml::render::Render;
    let renderer = ftml::render::html::HtmlRender;
    let html_output = renderer.render(&tree, &page_info, &settings);

    // 8. 大功告成！提取包裹里的 body 字段并返回！
    Ok(html_output.body.to_string())
}

#[pymodule]
fn ftml_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render_wikidot_to_html, m)?)?;
    Ok(())
}