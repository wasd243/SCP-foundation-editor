use regex::Regex;

/// This function attaches the `data-editor-export` meta to all `[[span]]` blocks for exporter generation.
pub fn attach_span_meta_data(text: &str) -> String {
    let re_span = Regex::new(r"(?i)\[\[span(?:\s+([^\]]*?))?]]").unwrap();

    if !re_span.is_match(text) {
        return text.into();
    }

    re_span
        .replace_all(text, |captures: &regex::Captures| {
            let attrs = captures.get(1).map_or("", |matched| matched.as_str());

            if attrs.to_lowercase().contains("data-editor-export") {
                return captures
                    .get(0)
                    .map_or("", |matched| matched.as_str())
                    .to_string();
            }

            if attrs.trim().is_empty() {
                r#"[[span data-editor-export="span"]]"#.to_string()
            } else {
                format!(r#"[[span data-editor-export="span" {attrs}]]"#)
            }
        })
        .into_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_export_meta_to_span_with_attrs() {
        assert_eq!(
            attach_span_meta_data(r#"[[span class="block"]]"#),
            r#"[[span data-editor-export="span" class="block"]]"#
        );
    }

    #[test]
    fn adds_export_meta_to_span_without_attrs() {
        assert_eq!(
            attach_span_meta_data("[[span]]"),
            r#"[[span data-editor-export="span"]]"#
        );
    }

    #[test]
    fn keeps_existing_export_meta() {
        assert_eq!(
            attach_span_meta_data(r#"[[span data-editor-export="span" class="block"]]"#),
            r#"[[span data-editor-export="span" class="block"]]"#
        );
    }
}
