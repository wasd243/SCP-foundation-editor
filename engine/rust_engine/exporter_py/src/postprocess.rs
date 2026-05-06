use crate::theme::snapshot_bool;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use regex::{Captures, Regex};
use std::collections::HashSet;

fn flatten_sizes(mut text: String) -> String {
    let nested_size_re = Regex::new(
        r"(?is)(\[\[size\s+[^\]]+\]\])(.*?)\[\[size\s+[^\]]+\]\](.*?)\[\[/size\]\](.*?)(\[\[/size\]\])",
    )
    .expect("valid regex");
    let adjacent_size_re = Regex::new(
        r"(?is)\[\[size\s+[^\]]+\]\](.*?)\[\[/size\]\]\s*\[\[size\s+([^\]]+)\]\](.*?)\[\[/size\]\]",
    )
    .expect("valid regex");

    loop {
        let new_text = nested_size_re
            .replace_all(&text, "$1$2$3$4$5")
            .into_owned();
        let new_text = adjacent_size_re
            .replace_all(&new_text, "[[size $2]]$1$3[[/size]]")
            .into_owned();
        if new_text == text {
            break;
        }
        text = new_text;
    }
    text
}

pub fn cleanup_body(raw_body: &str) -> String {
    let mut body = raw_body.replace("\r\n", "\n").replace('\u{00A0}', " ");
    body = Regex::new(r"(?i)\[\[toc\]\]\s*")
        .expect("valid regex")
        .replace_all(&body, "")
        .into_owned();
    body = Regex::new(r"([^\n])\s*(\[\[include component:image-block)")
        .expect("valid regex")
        .replace_all(&body, "$1\n$2")
        .into_owned();
    body = Regex::new(r"(?m)^[ \t]+(\[\[include component:image-block)")
        .expect("valid regex")
        .replace_all(&body, "$1")
        .into_owned();

    while body.contains("@@@@\n\n@@@@") {
        body = body.replace("@@@@\n\n@@@@", "@@@@\n@@@@");
    }
    body = Regex::new(r"\n\n(@@@@)")
        .expect("valid regex")
        .replace_all(&body, "\n$1")
        .into_owned();
    body = Regex::new(r"(@@@@)\n\n")
        .expect("valid regex")
        .replace_all(&body, "$1\n")
        .into_owned();
    body = Regex::new(r"\[\[<\]\]")
        .expect("valid regex")
        .replace_all(&body, "")
        .into_owned();
    body = Regex::new(r"\[\[/<\]\]")
        .expect("valid regex")
        .replace_all(&body, "")
        .into_owned();

    body = Regex::new(r#"(?s)(\[\[/div\]\])([\s@]+)(\[\[div\s+class=["'](?:dark)?document.*?\]\])"#)
        .expect("valid regex")
        .replace_all(&body, |caps: &Captures<'_>| {
            if caps[2].matches("@@@@").count() <= 1 {
                format!("{}\n{}", &caps[1], &caps[3])
            } else {
                caps[0].to_string()
            }
        })
        .into_owned();

    body = flatten_sizes(body);
    Regex::new(r"(?i)##(?:black|#000000|#000)\|([^#]*?)##")
        .expect("valid regex")
        .replace_all(&body, "$1")
        .into_owned()
}

pub fn finalize_output(
    mut head_styles_code: String,
    mut final_code: String,
    license_code: &str,
    snapshot: &Bound<'_, PyDict>,
) -> String {
    final_code.push_str(license_code);

    if snapshot_bool(snapshot, "mono_security_on", true) {
        final_code = Regex::new(r"\{\{([^{}]*[\u4e00-\u9fa5]+[^{}]*)\}\}")
            .expect("valid regex")
            .replace_all(&final_code, "$1")
            .into_owned();
    }

    head_styles_code.push_str(&final_code);
    let css_pattern = Regex::new(r"(?is)\[\[module CSS\]\]\n?(.*?)\n?\[\[/module\]\]")
        .expect("valid regex");
    let mut seen_css_contents = HashSet::new();

    let mut combined = css_pattern
        .replace_all(&head_styles_code, |caps: &Captures<'_>| {
            let block = caps[1].trim();
            if block.is_empty() || seen_css_contents.contains(block) {
                return String::new();
            }
            seen_css_contents.insert(block.to_string());
            format!("[[module CSS]]\n{}\n[[/module]]", block)
        })
        .into_owned();

    combined = Regex::new(r"\n{3,}")
        .expect("valid regex")
        .replace_all(&combined, "\n\n")
        .into_owned();
    combined.trim().to_string()
}
