use regex::Regex;

use super::model::{BASALT_SPECIAL_MAP, BasaltDivData, BasaltDivKind};

pub fn extract_top_div(txt: &str, start_pos: usize) -> Option<(String, String, usize)> {
    if start_pos >= txt.len() {
        println!("[PARSER] start_pos >= txt.len()");
        return None;
    }

    let tag_end = txt[start_pos..]
        .find("]]")
        .map(|offset| start_pos + offset)?;
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

pub fn parse_basalt_div_data(txt: &str, start_pos: usize) -> Option<BasaltDivData> {
    let (params, inner_content, end_pos) = extract_top_div(txt, start_pos)?;
    let class_match = Regex::new(r#"class=["']([^"']+)["']"#)
        .unwrap()
        .captures(&params)?;
    let classes = class_match
        .get(1)?
        .as_str()
        .split_whitespace()
        .map(|cls| cls.to_string())
        .collect();

    Some(BasaltDivData {
        classes,
        source_div: txt[start_pos..end_pos].to_string(),
        inner_content,
        end_pos,
    })
}

pub fn classify(classes: &[String]) -> Option<BasaltDivKind> {
    if classes.iter().any(|cls| cls == "floatbox") {
        return Some(BasaltDivKind::Floatbox {
            right: classes.iter().any(|cls| cls == "right"),
        });
    }

    classes.iter().find_map(|cls| {
        BASALT_SPECIAL_MAP
            .iter()
            .find(|(class_name, _)| *class_name == cls)
            .map(|(_, box_class)| BasaltDivKind::Special {
                primary_class: cls.clone(),
                box_class,
            })
    })
}
