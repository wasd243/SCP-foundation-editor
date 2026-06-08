use regex::Regex;
use std::fs;

const CSS_CACHE_DIR: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp");
const CSS_CACHE_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/user_css.css");

/// Extracts the CSS from the ftml and saves it to a file.
/// The exporter will read `user_css.css` to generate `[[module css]]` blocks.
/// When users are not entering module css, the cacher will export
/// ```css
/// /* NO USER CSS */
/// ```
pub fn css_cacher(ftml: &str) {
    let re = Regex::new(r"(?is)\[\[module css]](.*?)\[\[/module]]").unwrap();
    let css = re
        .captures_iter(ftml)
        .filter_map(|captures| captures.get(1))
        .map(|css_match| css_match.as_str())
        .collect::<Vec<_>>()
        .join("\n");

    let css = if css.trim().is_empty() {
        "\n/* NO USER CSS */\n".to_string()
    } else {
        css
    };

    fs::create_dir_all(CSS_CACHE_DIR).unwrap();

    fs::write(CSS_CACHE_PATH, css).unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_css_cacher() {
        let ftml = r#"
        [[module css]]
        .test {
        border: 1px solid red;
        }
        [[/module]]
        //Other contents here.//
        "#;
        css_cacher(ftml);
    }
}
