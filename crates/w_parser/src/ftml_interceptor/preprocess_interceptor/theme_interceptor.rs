use regex::Regex;
use serde::{Deserialize, Serialize};
use std::fs;
use once_cell::sync::Lazy;
use std::sync::Mutex;

pub static THEME_CACHE: Lazy<Mutex<String>> = Lazy::new(|| Mutex::new(String::new()));

/// This constant is public for the whole project to use.
pub const THEME_STATUS_TEMP_PATH: &str =
    concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/theme_status.json");

/// Root directory of the resource pack themes, where theme `.ftml` files live.
pub const RESOURCEPACK_THEMES_PATH: &str =
    concat!(env!("CARGO_MANIFEST_DIR"), "/../../resourcepack/themes");

#[derive(Serialize, Deserialize, Debug)]
pub struct ThemeStatus {
    pub theme: bool,
    pub theme_name: Option<String>,
    pub parent_theme: Option<bool>,
    pub parent_theme_name: Vec<String>,
}

pub fn theme_interceptor(ftml: &str) -> String {
    // This regex matches any `[[include :theme:...]]`
    let re = Regex::new(r"\s*\[\[include\s+:[^\]]*?:theme:[^\]]*?\]\]").unwrap();

    // Preprocess here
    let theme_path = generate_theme_path(ftml);
    let theme_name = extract_theme_name(ftml);
    let (parent_theme, parent_theme_name) = detect_parent_theme(theme_path.as_deref());
    let full_css = wiki_css::preprocess(ftml);

    // Cache the full CSS here in memory
    *THEME_CACHE.lock().unwrap() = full_css;

    write_theme_status(
        re.is_match(ftml),
        theme_name,
        parent_theme,
        parent_theme_name,
    );

    re.replace_all(ftml, "").to_string()
}

/// Detects the parent theme by reading the theme `.ftml` file at `theme_path`
/// and matching the `~_PARENT_THEME=<name>_~` marker.
///
/// Returns `(parent_theme, parent_theme_name)`:
/// - a single real name (e.g. `~_PARENT_THEME=parallel_~`) -> `(true, ["parallel"])`
/// - `~_PARENT_THEME=null_~`, no marker, multiple markers, or an unreadable
///   file -> the default `(false, [])`
///
/// Only one parent theme is supported for now; multiple markers fall back to
/// the default.
fn detect_parent_theme(theme_path: Option<&str>) -> (bool, Vec<String>) {
    let default = (false, Vec::new());

    let Some(path) = theme_path else {
        return default;
    };
    let Ok(content) = fs::read_to_string(path) else {
        return default;
    };

    let re = Regex::new(r"~_PARENT_THEME=([\w-]+)_~").unwrap();
    let names: Vec<String> = re
        .captures_iter(&content)
        .map(|caps| caps[1].to_string())
        .collect();

    match names.as_slice() {
        [name] if name != "null" => (true, vec![name.clone()]),
        _ => default,
    }
}

/// Extracts the theme name from the theme include in `ftml`, if any.
///
/// e.g. `[[include :scp-wiki-cn:theme:yore]]` -> `Some("yore")`.
fn extract_theme_name(ftml: &str) -> Option<String> {
    let re = Regex::new(r"\[\[include\s+:[\w-]+:theme:([\w-]+)").unwrap();
    re.captures(ftml).map(|caps| caps[1].to_string())
}

/// Maps a Wikidot site slug to its resource pack branch directory.
fn site_to_branch(site: &str) -> &str {
    match site {
        "scp-wiki" => "EN",
        "scp-wiki-cn" => "CN",
        other => other,
    }
}

/// Generates the resource pack path for the theme include in `ftml`, if any.
///
/// The site slug determines the branch directory and the theme name becomes
/// the file name, e.g.:
/// - `[[include :scp-wiki:theme:test]]`     -> `resourcepack/themes/EN/test.ftml`
/// - `[[include :scp-wiki-cn:theme:yore]]`  -> `resourcepack/themes/CN/yore.ftml`
fn generate_theme_path(ftml: &str) -> Option<String> {
    // Capture the site slug and the theme name out of the include.
    let re = Regex::new(r"\[\[include\s+:([\w-]+):theme:([\w-]+)").unwrap();
    let caps = re.captures(ftml)?;

    let branch = site_to_branch(&caps[1]);
    let theme_name = &caps[2];

    Some(format!(
        "{RESOURCEPACK_THEMES_PATH}/{branch}/{theme_name}.ftml"
    ))
}

/// Writes the theme status to the temp file. When a theme include is matched,
/// `theme` is `true` and `theme_name` holds the matched name; otherwise
/// `theme` is `false` and `theme_name` is `null`. `parent_theme` defaults to
/// `false` and `parent_theme_name` to `[]`.
fn write_theme_status(
    matched: bool,
    theme_name: Option<String>,
    parent_theme: bool,
    parent_theme_name: Vec<String>,
) {
    let status = ThemeStatus {
        theme: matched,
        theme_name,
        parent_theme: Some(parent_theme),
        parent_theme_name,
    };

    if let Ok(contents) = serde_json::to_string_pretty(&status) {
        let _ = fs::write(THEME_STATUS_TEMP_PATH, contents);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_theme_interceptor() {
        let ftml = r#"[[include :scp-wiki:theme:test]]"#;
        assert_eq!(theme_interceptor(ftml), "");
    }

    #[test]
    fn test_wired_theme_name_with_include_variables() {
        let ftml = r#"
        [[include :scp-wiki:theme:test
        |var1=value1
        |var2=value2]]"#;
        assert_eq!(theme_interceptor(ftml), "");
    }

    #[test]
    fn test_wired_theme_name_with_include_variables_without_newline() {
        let ftml = r#"[[include :scp-wiki:theme:test|var1=value1|var2=value2]]"#;
        assert_eq!(theme_interceptor(ftml), "");
    }

    #[test]
    fn test_normal_text() {
        let ftml = r#"This is a normal text."#;
        assert_eq!(theme_interceptor(ftml), ftml);
    }

    #[test]
    fn test_generate_theme_path_en() {
        let ftml = r#"[[include :scp-wiki:theme:test]]"#;
        assert_eq!(
            generate_theme_path(ftml),
            Some(format!("{RESOURCEPACK_THEMES_PATH}/EN/test.ftml"))
        );
    }

    #[test]
    fn test_generate_theme_path_cn() {
        let ftml = r#"[[include :scp-wiki-cn:theme:yore]]"#;
        assert_eq!(
            generate_theme_path(ftml),
            Some(format!("{RESOURCEPACK_THEMES_PATH}/CN/yore.ftml"))
        );
    }

    #[test]
    fn test_generate_theme_path_with_variables() {
        let ftml = r#"[[include :scp-wiki-cn:theme:parallel|var1=value1]]"#;
        assert_eq!(
            generate_theme_path(ftml),
            Some(format!("{RESOURCEPACK_THEMES_PATH}/CN/parallel.ftml"))
        );
    }

    #[test]
    fn test_generate_theme_path_no_theme() {
        let ftml = r#"This is a normal text."#;
        assert_eq!(generate_theme_path(ftml), None);
    }

    #[test]
    fn test_extract_theme_name() {
        let ftml = r#"[[include :scp-wiki-cn:theme:yore]]"#;
        assert_eq!(extract_theme_name(ftml), Some("yore".to_string()));
    }

    #[test]
    fn test_extract_theme_name_with_variables() {
        let ftml = r#"[[include :scp-wiki:theme:test|var1=value1]]"#;
        assert_eq!(extract_theme_name(ftml), Some("test".to_string()));
    }

    #[test]
    fn test_extract_theme_name_no_theme() {
        let ftml = r#"This is a normal text."#;
        assert_eq!(extract_theme_name(ftml), None);
    }

    #[test]
    fn test_detect_parent_theme_with_parent() {
        // CN/yore.ftml declares `~_PARENT_THEME=parallel_~`.
        let path = format!("{RESOURCEPACK_THEMES_PATH}/CN/yore.ftml");
        assert_eq!(
            detect_parent_theme(Some(&path)),
            (true, vec!["parallel".to_string()])
        );
    }

    #[test]
    fn test_detect_parent_theme_null() {
        // CN/parallel.ftml declares `~_PARENT_THEME=null_~`.
        let path = format!("{RESOURCEPACK_THEMES_PATH}/CN/parallel.ftml");
        assert_eq!(detect_parent_theme(Some(&path)), (false, vec![]));
    }

    #[test]
    fn test_detect_parent_theme_no_path() {
        assert_eq!(detect_parent_theme(None), (false, vec![]));
    }

    #[test]
    fn test_detect_parent_theme_missing_file() {
        let path = format!("{RESOURCEPACK_THEMES_PATH}/CN/does_not_exist.ftml");
        assert_eq!(detect_parent_theme(Some(&path)), (false, vec![]));
    }

    #[test]
    fn test_the_whole_interceptor() {
        let ftml = r#"[[include :scp-wiki-cn:theme:parallel]]"#;
        theme_interceptor(ftml); // There's no assertion here, just make sure it will cache theme status
    }

    #[test]
    fn test_the_whole_interceptor_with_parent_theme() {
        let ftml = r#"[[include :scp-wiki-cn:theme:yore]]"#;
        theme_interceptor(ftml); // There's no assertion here, just make sure it will cache theme status
    }
}
