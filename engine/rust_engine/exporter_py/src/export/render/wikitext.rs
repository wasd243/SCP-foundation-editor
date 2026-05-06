use crate::export::ast::ExportTree;
use crate::export::render::Render;
use std::collections::HashSet;

#[derive(Debug, Default)]
pub struct WikitextRender;

impl Render for WikitextRender {
    type Output = String;

    fn render(&self, tree: &ExportTree) -> String {
        if !tree.has_root {
            return String::new();
        }

        let mut head_styles = tree.styles_text();
        if tree.has_email_example && !head_styles.contains(email_css_block().trim()) {
            head_styles.push_str(email_css_block());
        }

        let mut final_code = tree.top_text();
        final_code.push_str(&cleanup_body(&tree.body_text()));
        final_code.push_str(&tree.license_text());

        if tree.mono_security {
            final_code = remove_mono_chinese_braces(&final_code);
        }

        let mut combined = format!("{}{}", head_styles, final_code);
        combined = dedup_css_modules(&combined);
        compress_newlines(combined.trim())
    }
}

fn email_css_block() -> &'static str {
    "[[module CSS]]\n\
.email-example .collapsible-block-folded a.collapsible-block-link {\n\
    animation: blink 0.8s ease-in-out infinite alternate;\n\
}\n\
@keyframes blink {\n\
    0% { color: transparent; }\n\
    50%, 100% { color: #b01; }\n\
}\n\
.email {border: solid 2px #000000; width: 88%; padding: 1px 15px; margin: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.5)}\n\
.email-example a.collapsible-block-link {font-weight: bold;}\n\
.tofrom {margin-left: 10px; margin-top: 5px; padding: 1px 15px; border-left: solid 3px maroon}\n\
[[/module]]\n"
}

fn find_ci(text: &str, needle: &str, start: usize) -> Option<usize> {
    if start >= text.len() {
        return None;
    }
    let hay = text[start..].to_ascii_lowercase();
    let nee = needle.to_ascii_lowercase();
    hay.find(&nee).map(|i| start + i)
}

fn starts_with_ci(text: &str, index: usize, needle: &str) -> bool {
    text.get(index..index + needle.len())
        .map(|s| s.eq_ignore_ascii_case(needle))
        .unwrap_or(false)
}

fn remove_toc_blocks(mut text: String) -> String {
    let token = "[[toc]]";
    while let Some(pos) = find_ci(&text, token, 0) {
        let mut end = pos + token.len();
        while let Some(ch) = text[end..].chars().next() {
            if ch.is_whitespace() {
                end += ch.len_utf8();
            } else {
                break;
            }
        }
        text.replace_range(pos..end, "");
    }
    text
}

fn normalize_image_block_spacing(text: &str) -> String {
    let token = "[[include component:image-block";
    let mut out = String::new();
    for line in text.lines() {
        if let Some(pos) = line.find(token) {
            let left = &line[..pos];
            let right = &line[pos..];
            if left.trim().is_empty() {
                out.push_str(right.trim_start());
                out.push('\n');
            } else {
                out.push_str(left.trim_end());
                out.push('\n');
                out.push_str(right.trim_start());
                out.push('\n');
            }
        } else {
            out.push_str(line);
            out.push('\n');
        }
    }
    if !text.ends_with('\n') && out.ends_with('\n') {
        out.pop();
    }
    out
}

fn normalize_document_div_gap(text: &str) -> String {
    let mut out = String::new();
    let mut i = 0usize;
    while let Some(rel) = text[i..].find("[[/div]]") {
        let start = i + rel;
        let div_end = start + "[[/div]]".len();
        out.push_str(&text[i..div_end]);

        let mut j = div_end;
        let mut at_count = 0usize;
        while j < text.len() {
            if text[j..].starts_with("@@@@") {
                at_count += 1;
                j += 4;
                continue;
            }
            let ch = match text[j..].chars().next() {
                Some(c) => c,
                None => break,
            };
            if ch.is_whitespace() || ch == '@' {
                j += ch.len_utf8();
                continue;
            }
            break;
        }

        let is_doc = text[j..].starts_with("[[div class=\"document")
            || text[j..].starts_with("[[div class='document")
            || text[j..].starts_with("[[div class=\"darkdocument")
            || text[j..].starts_with("[[div class='darkdocument");

        if is_doc && at_count <= 1 {
            out.push('\n');
            i = j;
        } else {
            out.push_str(&text[div_end..j]);
            i = j;
        }
    }
    out.push_str(&text[i..]);
    out
}

#[derive(Clone)]
struct SizeBlock {
    open: String,
    content: String,
}

fn flatten_nested_sizes(text: &str) -> String {
    let mut out = String::new();
    let mut i = 0usize;
    let mut depth = 0usize;

    while i < text.len() {
        if starts_with_ci(text, i, "[[size ") && let Some(close_rel) = text[i..].find("]]") {
            let end = i + close_rel + 2;
            if depth == 0 {
                out.push_str(&text[i..end]);
            }
            depth += 1;
            i = end;
            continue;
        }
        if starts_with_ci(text, i, "[[/size]]") {
            if depth > 1 {
                depth -= 1;
                i += "[[/size]]".len();
                continue;
            }
            if depth == 1 {
                depth = 0;
                out.push_str("[[/size]]");
                i += "[[/size]]".len();
                continue;
            }
        }
        if let Some(ch) = text[i..].chars().next() {
            out.push(ch);
            i += ch.len_utf8();
        } else {
            break;
        }
    }
    out
}

fn parse_size_block(text: &str, start: usize) -> Option<(usize, SizeBlock)> {
    if !starts_with_ci(text, start, "[[size ") {
        return None;
    }
    let open_end_rel = text[start..].find("]]")?;
    let open_end = start + open_end_rel + 2;
    let close_start = find_ci(text, "[[/size]]", open_end)?;
    let close_end = close_start + "[[/size]]".len();
    Some((
        close_end,
        SizeBlock {
            open: text[start..open_end].to_string(),
            content: text[open_end..close_start].to_string(),
        },
    ))
}

fn merge_adjacent_size_blocks(text: &str) -> String {
    let mut out = String::new();
    let mut i = 0usize;
    let mut pending: Option<SizeBlock> = None;
    let mut gap = String::new();

    while i < text.len() {
        if let Some((end, block)) = parse_size_block(text, i) {
            if let Some(prev) = pending.take() {
                if gap.trim().is_empty() {
                    pending = Some(SizeBlock {
                        open: block.open,
                        content: format!("{}{}", prev.content, block.content),
                    });
                    gap.clear();
                } else {
                    out.push_str(&prev.open);
                    out.push_str(&prev.content);
                    out.push_str("[[/size]]");
                    out.push_str(&gap);
                    pending = Some(block);
                    gap.clear();
                }
            } else {
                pending = Some(block);
            }
            i = end;
            continue;
        }

        let next = find_ci(text, "[[size ", i).unwrap_or(text.len());
        let chunk = &text[i..next];
        if let Some(prev) = pending.take() {
            if chunk.trim().is_empty() {
                pending = Some(prev);
                gap.push_str(chunk);
            } else {
                out.push_str(&prev.open);
                out.push_str(&prev.content);
                out.push_str("[[/size]]");
                out.push_str(&gap);
                out.push_str(chunk);
                gap.clear();
            }
        } else {
            out.push_str(chunk);
        }
        i = next;
    }

    if let Some(prev) = pending {
        out.push_str(&prev.open);
        out.push_str(&prev.content);
        out.push_str("[[/size]]");
        out.push_str(&gap);
    }
    out
}

fn remove_empty_black_color_tags(text: &str) -> String {
    let mut out = String::new();
    let mut i = 0usize;
    while let Some(start_rel) = text[i..].find("##") {
        let start = i + start_rel;
        out.push_str(&text[i..start]);
        let body_start = start + 2;
        let Some(end_rel) = text[body_start..].find("##") else {
            out.push_str(&text[start..]);
            return out;
        };
        let end = body_start + end_rel;
        let inner = &text[body_start..end];
        if let Some(pipe) = inner.find('|') {
            let color = inner[..pipe].trim().to_ascii_lowercase();
            if color == "black" || color == "#000000" || color == "#000" {
                out.push_str(&inner[pipe + 1..]);
            } else {
                out.push_str("##");
                out.push_str(inner);
                out.push_str("##");
            }
        } else {
            out.push_str("##");
            out.push_str(inner);
            out.push_str("##");
        }
        i = end + 2;
    }
    out.push_str(&text[i..]);
    out
}

fn contains_cjk(s: &str) -> bool {
    s.chars().any(|c| ('\u{4E00}'..='\u{9FA5}').contains(&c))
}

fn remove_mono_chinese_braces(text: &str) -> String {
    let mut out = String::new();
    let mut i = 0usize;
    while let Some(start_rel) = text[i..].find("{{") {
        let start = i + start_rel;
        out.push_str(&text[i..start]);
        let content_start = start + 2;
        let Some(end_rel) = text[content_start..].find("}}") else {
            out.push_str(&text[start..]);
            return out;
        };
        let end = content_start + end_rel;
        let inner = &text[content_start..end];
        if contains_cjk(inner) {
            out.push_str(inner);
        } else {
            out.push_str("{{");
            out.push_str(inner);
            out.push_str("}}");
        }
        i = end + 2;
    }
    out.push_str(&text[i..]);
    out
}

fn dedup_css_modules(text: &str) -> String {
    let mut out = String::new();
    let mut i = 0usize;
    let mut seen = HashSet::new();

    while let Some(start) = find_ci(text, "[[module css]]", i) {
        out.push_str(&text[i..start]);
        let open_end = match text[start..].find("]]") {
            Some(v) => start + v + 2,
            None => {
                out.push_str(&text[start..]);
                return out;
            }
        };
        let close_start = match find_ci(text, "[[/module]]", open_end) {
            Some(v) => v,
            None => {
                out.push_str(&text[start..]);
                return out;
            }
        };
        let content = text[open_end..close_start].trim();
        if !content.is_empty() && !seen.contains(content) {
            seen.insert(content.to_string());
            out.push_str("[[module CSS]]\n");
            out.push_str(content);
            out.push_str("\n[[/module]]");
        }
        i = close_start + "[[/module]]".len();
    }
    out.push_str(&text[i..]);
    out
}

fn compress_newlines(text: &str) -> String {
    let mut out = String::new();
    let mut nl = 0usize;
    for ch in text.chars() {
        if ch == '\n' {
            nl += 1;
            if nl <= 2 {
                out.push(ch);
            }
        } else {
            nl = 0;
            out.push(ch);
        }
    }
    out
}

fn cleanup_body(raw_body: &str) -> String {
    let mut body = raw_body.replace("\r\n", "\n").replace('\u{00A0}', " ");
    body = remove_toc_blocks(body);
    body = normalize_image_block_spacing(&body);
    while body.contains("@@@@\n\n@@@@") {
        body = body.replace("@@@@\n\n@@@@", "@@@@\n@@@@");
    }
    body = body.replace("\n\n@@@@", "\n@@@@").replace("@@@@\n\n", "@@@@\n");
    body = body.replace("[[<]]", "").replace("[[/<]]", "");
    body = normalize_document_div_gap(&body);
    body = flatten_nested_sizes(&body);
    body = merge_adjacent_size_blocks(&body);
    remove_empty_black_color_tags(&body)
}
