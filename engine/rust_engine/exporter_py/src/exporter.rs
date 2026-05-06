use crate::postprocess::{cleanup_body, finalize_output};
use crate::theme::{build_theme_and_rate, email_css_block, snapshot_bool};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};
use std::collections::HashSet;

const BLOCK_TAGS: [&str; 12] = [
    "div",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "blockquote",
    "table",
];

struct ExtractedData {
    has_root: bool,
    head_styles_code: String,
    has_rate_box: bool,
    rate_hidden: bool,
    rate_align: String,
    has_toc_anchor: bool,
    has_email_example: bool,
    raw_body: String,
    license_code: String,
}

fn get_attr_str(node: &Bound<'_, PyAny>, attr: &str, default: &str) -> PyResult<String> {
    node.call_method1("get", (attr, default))?.extract::<String>()
}

fn get_field_lic(node: &Bound<'_, PyAny>, field: &str) -> PyResult<String> {
    let selector = format!(r#"[data-field="{}"]"#, field);
    let el = node.call_method1("select_one", (selector,))?;
    if el.is_none() {
        return Ok(String::new());
    }
    let text = el.call_method0("get_text")?.call_method0("strip")?;
    text.extract::<String>()
}

fn parse_license_only(comp_node: &Bound<'_, PyAny>, use_better_footnotes: bool) -> PyResult<String> {
    let author = get_field_lic(comp_node, "author")?;
    let translator = get_field_lic(comp_node, "translator")?;
    let is_original = get_attr_str(comp_node, "data-original", "false")? == "true";

    let mut base_code = String::new();
    if !use_better_footnotes {
        base_code.push_str("[[footnoteblock]]\n");
    }
    base_code.push_str("[[include :scp-wiki-cn:component:license-box\n");
    if is_original {
        base_code.push_str("|lang=CN\n");
    }
    if !author.is_empty() {
        base_code.push_str(&format!("|author={}\n", author));
    }
    if !is_original && !translator.is_empty() {
        base_code.push_str(&format!("|translator={}\n", translator));
    }
    base_code.push_str("]]\n=====\n");

    let file_entries = comp_node.call_method1("select", (".file-entry",))?;
    let total = file_entries.len().unwrap_or(0);
    let fields = [
        ("文件名", "file_name"),
        ("图像名", "img_name"),
        ("图像作者", "img_author"),
        ("授权协议", "img_license"),
        ("来源链接", "source_link"),
        ("衍生自", "derived_from"),
        ("备注", "note"),
    ];

    let mut files_code = String::new();
    for (idx, entry_item) in file_entries.iter()?.enumerate() {
        let entry = entry_item?;
        let mut has_any_field = false;
        let mut file_text = String::new();
        let img_name_val = get_field_lic(&entry, "img_name")?;
        let img_author_val = get_field_lic(&entry, "img_author")?;

        for (label, key) in fields {
            let val = get_field_lic(&entry, key)?;
            if val.is_empty() {
                continue;
            }
            has_any_field = true;
            let mut real_label = label.to_string();
            if key == "img_author" && img_name_val.is_empty() && !img_author_val.is_empty() {
                real_label = "作者".to_string();
            }

            if real_label == "来源链接" {
                file_text.push_str(&format!("> {}：{}\n", real_label, val));
            } else {
                file_text.push_str(&format!("> **{}：**{}\n", real_label, val));
            }
        }

        if has_any_field {
            files_code.push_str(&file_text);
            if idx + 1 < total {
                files_code.push('\n');
            }
        }
    }

    Ok(format!(
        "{}{}=====\n[[include :scp-wiki-cn:component:license-box-end]]\n",
        base_code, files_code
    ))
}

fn extract_data(
    py: Python<'_>,
    html: &str,
    snapshot: &Bound<'_, PyDict>,
) -> PyResult<ExtractedData> {
    let bs4 = py.import_bound("bs4")?;
    let beautiful_soup = bs4.getattr("BeautifulSoup")?;
    let navigable_string = bs4.getattr("NavigableString")?;
    let parse_node = py
        .import_bound("formats.wikidot.parse_node.parse_node")?
        .getattr("handle_parse_node")?;

    let soup = beautiful_soup.call1((html, "html.parser"))?;

    let root_kwargs = PyDict::new_bound(py);
    root_kwargs.set_item("id", "editor-root")?;
    let root = soup.call_method("find", (), Some(&root_kwargs))?;
    if root.is_none() {
        return Ok(ExtractedData {
            has_root: false,
            head_styles_code: String::new(),
            has_rate_box: false,
            rate_hidden: false,
            rate_align: String::new(),
            has_toc_anchor: false,
            has_email_example: false,
            raw_body: String::new(),
            license_code: String::new(),
        });
    }

    let mut head_styles_code = String::new();
    let mut seen_css_blocks = HashSet::new();
    let empty_state = PyDict::new_bound(py);
    let styles = soup.call_method1("find_all", ("style",))?;
    for style_item in styles.iter()? {
        let style_tag = style_item?;
        if get_attr_str(&style_tag, "data-no-hoist", "")? == "true" {
            continue;
        }

        let parsed = parse_node.call1((style_tag.clone(), empty_state.clone()))?;
        let css_content = parsed.extract::<String>().unwrap_or_default().trim().to_string();
        if !css_content.is_empty()
            && !seen_css_blocks.contains(&css_content)
            && !css_content.contains("[[module Rate]]")
        {
            seen_css_blocks.insert(css_content.clone());
            head_styles_code.push_str(&css_content);
            head_styles_code.push('\n');
        }
        style_tag.call_method0("decompose")?;
    }

    let rate_box = soup.call_method1("select_one", (".rate-module-box",))?;
    let has_rate_box = !rate_box.is_none();
    let mut rate_hidden = false;
    let mut rate_align = String::new();
    if has_rate_box {
        rate_hidden = get_attr_str(&rate_box, "data-hidden", "false")? == "true";
        rate_align = get_attr_str(&rate_box, "data-align", "")?;
        rate_box.call_method0("decompose")?;
    }

    let parse_state = PyDict::new_bound(py);
    parse_state.set_item("better_footnotes", snapshot_bool(snapshot, "bf_on", false))?;
    parse_state.set_item(
        "mono_security",
        snapshot_bool(snapshot, "mono_security_on", true),
    )?;
    parse_state.set_item(
        "line_break_symbol_lock",
        snapshot_bool(snapshot, "line_break_symbol_lock_on", false),
    )?;

    let attrs = PyDict::new_bound(py);
    attrs.set_item("data-type", "license")?;
    let license_kwargs = PyDict::new_bound(py);
    license_kwargs.set_item("attrs", attrs)?;
    let license_comps = root.call_method("find_all", (), Some(&license_kwargs))?;
    let mut license_code = String::new();
    for comp_item in license_comps.iter()? {
        let comp = comp_item?;
        license_code.push_str(&parse_license_only(
            &comp,
            snapshot_bool(snapshot, "bf_on", false),
        )?);
        comp.call_method0("decompose")?;
    }

    let contents = root.getattr("contents")?;
    let mut body_parts: Vec<String> = Vec::new();
    for item in contents.iter()? {
        let c: Bound<'_, PyAny> = item?;
        if c.is_instance(&navigable_string)? {
            let c_str = c.str()?.to_string_lossy().to_string();
            if c_str.trim().is_empty() {
                continue;
            }
        }

        let mut parsed = parse_node
            .call1((c.clone(), parse_state.clone()))?
            .extract::<String>()?;
        let name = match c.getattr("name") {
            Ok(v) => v.extract::<String>().unwrap_or_default(),
            Err(_) => String::new(),
        };
        if BLOCK_TAGS.contains(&name.as_str())
            && !parsed.starts_with('\n')
            && body_parts
                .last()
                .map(|s| !s.ends_with('\n'))
                .unwrap_or(false)
        {
            parsed = format!("\n{}", parsed);
        }
        body_parts.push(parsed);
    }

    let has_toc_anchor = html.contains("data-toc-anchor");
    let has_email_example = !soup
        .call_method1("select_one", (".email-example-box",))?
        .is_none();

    Ok(ExtractedData {
        has_root: true,
        head_styles_code,
        has_rate_box,
        rate_hidden,
        rate_align,
        has_toc_anchor,
        has_email_example,
        raw_body: body_parts.join(""),
        license_code,
    })
}

#[pyfunction]
pub fn export_html_to_wikidot(
    py: Python<'_>,
    html: &str,
    snapshot: &Bound<'_, PyDict>,
) -> PyResult<String> {
    let data = extract_data(py, html, snapshot)?;
    if !data.has_root {
        return Ok(String::new());
    }

    let mut final_code = build_theme_and_rate(
        snapshot,
        data.has_rate_box,
        data.rate_hidden,
        &data.rate_align,
        data.has_toc_anchor,
    );

    let mut head_styles_code = data.head_styles_code;
    if data.has_email_example {
        let key = email_css_block().trim().to_string();
        if !head_styles_code.contains(&key) {
            head_styles_code.push_str(email_css_block());
        }
    }

    final_code.push_str(&cleanup_body(&data.raw_body));
    Ok(finalize_output(
        head_styles_code,
        final_code,
        &data.license_code,
        snapshot,
    ))
}
