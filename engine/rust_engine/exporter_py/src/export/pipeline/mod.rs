use crate::export::ast::{BodyNodeKind, ExportTree, NodeSource, TopModuleKind};
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

fn snapshot_bool(snapshot: &Bound<'_, PyDict>, key: &str, default: bool) -> bool {
    snapshot
        .get_item(key)
        .ok()
        .flatten()
        .and_then(|v| v.extract::<bool>().ok())
        .unwrap_or(default)
}

fn build_top_modules(
    snapshot: &Bound<'_, PyDict>,
    has_rate_box: bool,
    rate_hidden: bool,
    rate_align: &str,
    has_toc_anchor: bool,
) -> Vec<(TopModuleKind, String)> {
    let mut out: Vec<(TopModuleKind, String)> = Vec::new();

    if snapshot_bool(snapshot, "basalt_on", false) {
        let mut opts = Vec::new();
        if snapshot_bool(snapshot, "basalt_dark", false) {
            opts.push("darkmode=a");
        }
        if snapshot_bool(snapshot, "basalt_wide", false) {
            opts.push("wide=a");
        }
        if snapshot_bool(snapshot, "basalt_hide", false) {
            opts.push("hidetitle=a");
        }
        if opts.is_empty() {
            out.push((TopModuleKind::Theme, "[[include :scp-wiki-cn:theme:basalt]]\n".to_string()));
        } else {
            out.push((
                TopModuleKind::Theme,
                format!(
                    "[[include :scp-wiki-cn:theme:basalt 版式设置|{}]]\n",
                    opts.join("|")
                ),
            ));
        }
    } else if snapshot_bool(snapshot, "shiver_on", false) {
        let suffix = if snapshot_bool(snapshot, "shiv_mo", false) {
            " mo=*"
        } else if snapshot_bool(snapshot, "shiv_kl", false) {
            " kl=*"
        } else if snapshot_bool(snapshot, "shiv_dub", false) {
            " dub=*"
        } else if snapshot_bool(snapshot, "shiv_ct", false) {
            " ct=*"
        } else if snapshot_bool(snapshot, "shiv_ba", false) {
            " ba=*"
        } else {
            ""
        };
        out.push((
            TopModuleKind::Theme,
            format!("[[include :scp-wiki-cn:theme:shivering-night{}]]\n", suffix),
        ));
    } else if snapshot_bool(snapshot, "bhl_on", false) {
        out.push((
            TopModuleKind::Theme,
            "[[include :scp-wiki-cn:theme:black-highlighter-theme]]\n".to_string(),
        ));
        if snapshot_bool(snapshot, "bhl_sidebar", false) {
            out.push((
                TopModuleKind::Theme,
                "[[include :scp-wiki:component:bhl-dark-sidebar]]\n".to_string(),
            ));
        }
        if snapshot_bool(snapshot, "bhl_coll", false) {
            out.push((
                TopModuleKind::Theme,
                "[[include :scp-wiki:component:collapsible-sidebar]]\n".to_string(),
            ));
        }
        if snapshot_bool(snapshot, "bhl_toggle", false) {
            out.push((
                TopModuleKind::Theme,
                "[[include :scp-wiki:component:toggle-sidebar-bhl]]\n".to_string(),
            ));
        }
        if snapshot_bool(snapshot, "bhl_center", false) {
            out.push((
                TopModuleKind::Theme,
                "[[include :scp-wiki:component:centered-header-bhl]]\n".to_string(),
            ));
        }
        if snapshot_bool(snapshot, "bhl_office", false) {
            out.push((
                TopModuleKind::Theme,
                "[[include :scp-wiki-cn:theme:scp-offices-theme]]\n".to_string(),
            ));
        }
    }

    if has_rate_box && !rate_hidden {
        out.push((
            TopModuleKind::Rate,
            match rate_align {
                "left" => "[[<]]\n[[module Rate]]\n[[/<]]\n".to_string(),
                "right" => "[[>]]\n[[module Rate]]\n[[/>]]\n".to_string(),
                _ => "[[module Rate]]\n".to_string(),
            },
        ));
    }

    if snapshot_bool(snapshot, "bf_on", false) {
        out.push((
            TopModuleKind::BetterFootnotes,
            "[[include :scp-wiki-cn:component:betterfootnotes]]\n".to_string(),
        ));
    }
    if has_toc_anchor {
        out.push((TopModuleKind::Toc, "[[toc]]\n".to_string()));
    }
    out
}

fn get_attr_str(node: &Bound<'_, PyAny>, attr: &str, default: &str) -> String {
    node.call_method1("get", (attr, default))
        .and_then(|x| x.extract::<String>())
        .unwrap_or_else(|_| default.to_string())
}

fn get_field_lic(node: &Bound<'_, PyAny>, field: &str) -> String {
    let selector = format!(r#"[data-field="{}"]"#, field);
    match node.call_method1("select_one", (selector,)) {
        Ok(el) if !el.is_none() => el
            .call_method0("get_text")
            .and_then(|x| x.call_method0("strip"))
            .and_then(|x| x.extract::<String>())
            .unwrap_or_default(),
        _ => String::new(),
    }
}

fn parse_license_only(comp_node: &Bound<'_, PyAny>, use_better_footnotes: bool) -> String {
    let author = get_field_lic(comp_node, "author");
    let translator = get_field_lic(comp_node, "translator");
    let is_original = get_attr_str(comp_node, "data-original", "false") == "true";

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
    if let Ok(file_entries) = comp_node.call_method1("select", (".file-entry",)) {
        let total = file_entries.len().unwrap_or(0);
        if let Ok(iter) = file_entries.iter() {
            for (idx, entry_item) in iter.enumerate() {
                let Ok(entry) = entry_item else {
                    continue;
                };
                let mut has_any = false;
                let mut text = String::new();
                let img_name_val = get_field_lic(&entry, "img_name");
                let img_author_val = get_field_lic(&entry, "img_author");

                for (label, key) in fields {
                    let val = get_field_lic(&entry, key);
                    if val.is_empty() {
                        continue;
                    }
                    has_any = true;
                    let mut real_label = label.to_string();
                    if key == "img_author" && img_name_val.is_empty() && !img_author_val.is_empty() {
                        real_label = "作者".to_string();
                    }
                    if real_label == "来源链接" {
                        text.push_str(&format!("> {}：{}\n", real_label, val));
                    } else {
                        text.push_str(&format!("> **{}：**{}\n", real_label, val));
                    }
                }

                if has_any {
                    files_code.push_str(&text);
                    if idx + 1 < total {
                        files_code.push('\n');
                    }
                }
            }
        }
    }

    format!(
        "{}{}=====\n[[include :scp-wiki-cn:component:license-box-end]]\n",
        base_code, files_code
    )
}

fn fallback_node_text(node: &Bound<'_, PyAny>) -> String {
    node
        .call_method0("get_text")
        .and_then(|x| x.extract::<String>())
        .unwrap_or_default()
}

fn node_log_label(node: &Bound<'_, PyAny>) -> String {
    let tag = node
        .getattr("name")
        .ok()
        .and_then(|x| x.extract::<String>().ok())
        .unwrap_or_default();
    let id = get_attr_str(node, "id", "");
    if id.is_empty() {
        format!("<{}>", tag)
    } else {
        format!("<{} id=\"{}\">", tag, id)
    }
}

fn parse_node_with_fallback(
    parse_node: &Bound<'_, PyAny>,
    node: &Bound<'_, PyAny>,
    state: &Bound<'_, PyDict>,
) -> (NodeSource, String) {
    match parse_node
        .call1((node.clone(), state.clone()))
        .and_then(|x| x.extract::<String>())
    {
        Ok(parsed) if !parsed.trim().is_empty() => (NodeSource::ParseNode, parsed),
        Ok(_) => {
            let fallback = fallback_node_text(node);
            if fallback.trim().is_empty() {
                eprintln!(
                    "[exporter_py] dropped empty parse fallback for node {}",
                    node_log_label(node)
                );
            } else {
                eprintln!(
                    "[exporter_py] parse fallback used text for node {}",
                    node_log_label(node)
                );
            }
            (NodeSource::FallbackText, fallback)
        }
        Err(err) => {
            let fallback = fallback_node_text(node);
            if fallback.trim().is_empty() {
                eprintln!(
                    "[exporter_py] parse failed and fallback empty for node {}: {}",
                    node_log_label(node),
                    err
                );
            } else {
                eprintln!(
                    "[exporter_py] parse failed, fallback used text for node {}: {}",
                    node_log_label(node),
                    err
                );
            }
            (NodeSource::FallbackText, fallback)
        }
    }
}

fn classify_node_kind(tag_name: &str) -> BodyNodeKind {
    match tag_name {
        "div" | "p" | "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "ul" | "ol" | "blockquote"
        | "table" => BodyNodeKind::Block {
            tag: tag_name.to_string(),
        },
        "span" | "a" | "em" | "strong" | "b" | "i" | "u" | "sup" | "sub" | "code" => {
            BodyNodeKind::Inline {
                tag: tag_name.to_string(),
            }
        }
        "" => BodyNodeKind::Text,
        _ => BodyNodeKind::Unknown,
    }
}

pub fn build_export_tree(
    py: Python<'_>,
    html: &str,
    snapshot: &Bound<'_, PyDict>,
) -> PyResult<ExportTree> {
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
        return Ok(ExportTree::default());
    }

    let mut tree = ExportTree {
        has_root: true,
        mono_security: snapshot_bool(snapshot, "mono_security_on", true),
        ..ExportTree::default()
    };

    let mut seen_css_blocks = HashSet::new();
    let empty_state = PyDict::new_bound(py);
    let styles = soup.call_method1("find_all", ("style",))?;
    for style_item in styles.iter()? {
        let style_tag: Bound<'_, PyAny> = match style_item {
            Ok(x) => x,
            Err(_) => continue,
        };
        if get_attr_str(&style_tag, "data-no-hoist", "") == "true" {
            continue;
        }
        let (_source, parsed) = parse_node_with_fallback(&parse_node, &style_tag, &empty_state);
        let css_content = parsed.trim().to_string();
        if !css_content.is_empty()
            && !seen_css_blocks.contains(&css_content)
            && !css_content.contains("[[module Rate]]")
        {
            seen_css_blocks.insert(css_content.clone());
            tree.push_style(format!("{}\n", css_content));
        }
        let _ = style_tag.call_method0("decompose");
    }

    let rate_box = soup.call_method1("select_one", (".rate-module-box",))?;
    let has_rate_box = !rate_box.is_none();
    let mut rate_hidden = false;
    let mut rate_align = String::new();
    if has_rate_box {
        rate_hidden = get_attr_str(&rate_box, "data-hidden", "false") == "true";
        rate_align = get_attr_str(&rate_box, "data-align", "");
        let _ = rate_box.call_method0("decompose");
    }

    for (kind, wikidot) in build_top_modules(
        snapshot,
        has_rate_box,
        rate_hidden,
        &rate_align,
        html.contains("data-toc-anchor"),
    ) {
        tree.push_top_module(kind, wikidot);
    }

    tree.has_email_example = !soup
        .call_method1("select_one", (".email-example-box",))?
        .is_none();

    let use_bf = snapshot_bool(snapshot, "bf_on", false);
    let attrs = PyDict::new_bound(py);
    attrs.set_item("data-type", "license")?;
    let license_kwargs = PyDict::new_bound(py);
    license_kwargs.set_item("attrs", attrs)?;
    if let Ok(license_comps) = root.call_method("find_all", (), Some(&license_kwargs)) {
        for comp_item in license_comps.iter()? {
            let comp: Bound<'_, PyAny> = match comp_item {
                Ok(x) => x,
                Err(_) => continue,
            };
            tree.push_license(parse_license_only(&comp, use_bf));
            let _ = comp.call_method0("decompose");
        }
    }

    let parse_state = PyDict::new_bound(py);
    parse_state.set_item("better_footnotes", use_bf)?;
    parse_state.set_item("mono_security", tree.mono_security)?;
    parse_state.set_item(
        "line_break_symbol_lock",
        snapshot_bool(snapshot, "line_break_symbol_lock_on", false),
    )?;

    let contents = root.getattr("contents")?;
    for item in contents.iter()? {
        let node: Bound<'_, PyAny> = match item {
            Ok(x) => x,
            Err(_) => continue,
        };
        if node.is_instance(&navigable_string)? {
            let raw = node.str()?.to_string_lossy().to_string();
            if raw.trim().is_empty() {
                continue;
            }
        }

        let (source, mut parsed) = parse_node_with_fallback(&parse_node, &node, &parse_state);

        let tag_name = node
            .getattr("name")
            .ok()
            .and_then(|x| x.extract::<String>().ok())
            .unwrap_or_default();
        if BLOCK_TAGS.contains(&tag_name.as_str())
            && !parsed.starts_with('\n')
            && !tree.last_body_ends_with_newline()
        {
            parsed = format!("\n{}", parsed);
        }
        tree.push_body(classify_node_kind(&tag_name), source, parsed);
    }

    Ok(tree)
}

pub fn build_fallback_tree(
    py: Python<'_>,
    html: &str,
    snapshot: &Bound<'_, PyDict>,
) -> PyResult<ExportTree> {
    let bs4 = py.import_bound("bs4")?;
    let beautiful_soup = bs4.getattr("BeautifulSoup")?;
    let parse_node = py
        .import_bound("formats.wikidot.parse_node.parse_node")?
        .getattr("handle_parse_node")?;

    let soup = beautiful_soup.call1((html, "html.parser"))?;
    let root_kwargs = PyDict::new_bound(py);
    root_kwargs.set_item("id", "editor-root")?;
    let root = soup.call_method("find", (), Some(&root_kwargs))?;
    if root.is_none() {
        return Ok(ExportTree::default());
    }

    let mut tree = ExportTree {
        has_root: true,
        mono_security: snapshot_bool(snapshot, "mono_security_on", true),
        top_modules: Vec::new(),
        ..ExportTree::default()
    };
    for (kind, wikidot) in build_top_modules(snapshot, false, false, "", html.contains("data-toc-anchor")) {
        tree.push_top_module(kind, wikidot);
    }

    let parse_state = PyDict::new_bound(py);
    parse_state.set_item("better_footnotes", snapshot_bool(snapshot, "bf_on", false))?;
    parse_state.set_item("mono_security", tree.mono_security)?;
    parse_state.set_item(
        "line_break_symbol_lock",
        snapshot_bool(snapshot, "line_break_symbol_lock_on", false),
    )?;

    let contents = root.getattr("contents")?;
    for item in contents.iter()? {
        let node: Bound<'_, PyAny> = match item {
            Ok(x) => x,
            Err(_) => continue,
        };
        let (source, parsed) = parse_node_with_fallback(&parse_node, &node, &parse_state);
        let tag_name = node
            .getattr("name")
            .ok()
            .and_then(|x| x.extract::<String>().ok())
            .unwrap_or_default();
        tree.push_body(classify_node_kind(&tag_name), source, parsed);
    }

    Ok(tree)
}
