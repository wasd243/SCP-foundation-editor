use regex::Regex;

use super::model::FakeProtData;

pub fn extract_top_fakeprot_div(txt: &str, start_pos: usize) -> Option<(String, String, usize)> {
    let tag_end = txt[start_pos..].find("]]").map(|offset| start_pos + offset)?;
    let params_str = txt[start_pos + 5..tag_end].trim().to_string();
    let mut depth = 1;
    let mut i = tag_end + 2;

    while i < txt.len() && depth > 0 {
        let next_open = txt[i..].find("[[div").map(|offset| i + offset);
        let next_close = txt[i..].find("[[/div]]").map(|offset| i + offset);

        if next_close.is_none() {
            break;
        }

        match (next_open, next_close) {
            (Some(open_idx), Some(close_idx)) if open_idx < close_idx => {
                depth += 1;
                i = open_idx + 5;
            }
            (_, Some(close_idx)) => {
                depth -= 1;
                if depth == 0 {
                    let inner = txt[tag_end + 2..close_idx].to_string();
                    return Some((params_str, inner, close_idx + 8));
                }
                i = close_idx + 8;
            }
            _ => break,
        }
    }

    None
}

pub fn parse_fakeprot_data(txt: &str, start_pos: usize) -> Option<FakeProtData> {
    let (_params, inner_content, div_end) = extract_top_fakeprot_div(txt, start_pos)?;
    let login_id = Regex::new(r#"\*\s*default:\s*<([^>]+)>"#)
        .unwrap()
        .captures(&inner_content)
        .and_then(|caps| caps.get(1))
        .map(|m| m.as_str().trim().to_string())
        .unwrap_or_else(|| "你的ID".to_string());

    let coll_re = Regex::new(
        r#"(?is)^\s*\[\[collapsible\s+show="([^"]*)"\s+hide="([^"]*)"\]\](.*?)\[\[/collapsible\]\]"#,
    )
    .unwrap();
    let (collapsible_content, end_pos) = if let Some(caps) = coll_re.captures(&txt[div_end..]) {
        let content = caps.get(3).map(|m| m.as_str()).unwrap_or("文字").to_string();
        let end_pos = div_end + caps.get(0).unwrap().end();
        (content, end_pos)
    } else {
        ("文字".to_string(), div_end)
    };

    Some(FakeProtData {
        source: txt[start_pos..end_pos].to_string(),
        login_id,
        collapsible_content,
        end_pos,
    })
}
