mod resolve_import;

use regex::Regex;
use resolve_import::resolve_import;

pub fn preprocess(ftml: &str) -> String {
    // Strip leftover `~_..._~` notes (e.g. parent-theme markers).
    let ftml = sanitize_unused_notes(ftml);

    // 1. Remove `[[code ...]]` blocks that merely wrap a `[[module css]]`
    //    block. Such CSS is displayed as source code, not applied as a theme.
    let ftml = remove_code_wrapped_module_css(&ftml);

    // 2. Keep only real CSS blocks, discarding everything else.
    let ftml = keep_only_css_blocks(&ftml);

    // 3. Remove all invalid formats in the CSS file.
    let ftml = remove_unused_module_css(&ftml);

    // 4. Resolve `@import` rules, inlining them like a C preprocessor.
    resolve_import(&ftml)
}

fn sanitize_unused_notes(ftml: &str) -> String {
    let re = Regex::new(r"~_(.*?)_~").unwrap();
    re.replace_all(ftml, "").to_string()
}

/// Removes any `[[code ...]] ... [[module css]] ... [[/module]] ... [[/code]]`
/// block, i.e. a `[[module css]]` block nested inside a `[[code]]` block.
fn remove_code_wrapped_module_css(ftml: &str) -> String {
    let re =
        Regex::new(r"(?is)\[\[code(.*?)]](.*?)\[\[module css]](.*?)\[\[/module]](.*?)\[\[/code]]")
            .unwrap();
    re.replace_all(ftml, "").to_string()
}

/// Keeps only the actual CSS blocks, dropping everything else:
/// - `[[module css]] ... [[/module]]`
/// - `[[code type="css"]] ... [[/code]]`
fn keep_only_css_blocks(ftml: &str) -> String {
    let re = Regex::new(
        r#"(?is)\[\[module css]](.*?)\[\[/module]]|\[\[code type="css"]](.*?)\[\[/code]]"#,
    )
    .unwrap();
    re.find_iter(ftml)
        .map(|m| m.as_str())
        .collect::<Vec<_>>()
        .join("\n")
}

/// Remove all invalid formats in the CSS file, i.e. the block markers
/// `[[module css]]`, `[[/module]]`, `[[code type="css"]]`, and `[[/code]]`,
/// leaving only the raw CSS content.
fn remove_unused_module_css(ftml: &str) -> String {
    let re = Regex::new(
        r#"(?i)\[\[module css]]|\[\[/module]]|\[\[code type="css"]]|\[\[/code]]"#,
    )
    .unwrap();
    re.replace_all(ftml, "").to_string()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_preprocess() {
        let ftml = fs::read_to_string(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../resourcepack/themes/CN/parallel.ftml"
        ))
        .unwrap();
        println!("{}", preprocess(&ftml));
        fs::write(
            concat!(
                env!("CARGO_MANIFEST_DIR"),
                "/../../crates/wiki_css/test/parallel_test.css"
            ),
            preprocess(&ftml),
        )
        .unwrap();
    }
}
