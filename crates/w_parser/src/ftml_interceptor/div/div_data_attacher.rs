use regex::Regex;

/// This function attaches the `data-editor-export` meta to all `[[div]]` blocks for exporter generation.
pub fn attach_div_meta_data(text: &str) -> String {
    let re_div = Regex::new(r"(?i)\[\[div(?:\s+([^\]]*?))?]]").unwrap();

    if !re_div.is_match(text) {
        return text.into();
    }

    re_div
        .replace_all(text, |captures: &regex::Captures| {
            let attrs = captures.get(1).map_or("", |matched| matched.as_str());

            if attrs.to_lowercase().contains("data-editor-export") {
                return captures
                    .get(0)
                    .map_or("", |matched| matched.as_str())
                    .to_string();
            }

            if attrs.trim().is_empty() {
                r#"[[div data-editor-export="div"]]"#.to_string()
            } else {
                format!(r#"[[div data-editor-export="div" {attrs}]]"#)
            }
        })
        .into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_export_meta_to_div_with_attrs() {
        assert_eq!(
            attach_div_meta_data(r#"[[div class="block"]]"#),
            r#"[[div data-editor-export="div" class="block"]]"#
        );
    }

    #[test]
    fn adds_export_meta_to_div_without_attrs() {
        assert_eq!(
            attach_div_meta_data("[[div]]"),
            r#"[[div data-editor-export="div"]]"#
        );
    }

    #[test]
    fn keeps_existing_export_meta() {
        assert_eq!(
            attach_div_meta_data(r#"[[div data-editor-export="div" class="block"]]"#),
            r#"[[div data-editor-export="div" class="block"]]"#
        );
    }
}
