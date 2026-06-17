use regex::Regex;
use serde::{Deserialize, Serialize};
use std::fs;

/// This constant is public for the whole project to use.
pub const THEME_STATUS_TEMP_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/theme_status.json");

/// Root directory of the resource pack themes, where theme `.ftml` files live.
pub const RESOURCEPACK_THEMES_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../resourcepack/themes");

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
    let _theme_path = generate_theme_path(ftml);

    write_theme_boolean_status(re.is_match(ftml));

    re.replace_all(ftml, "").to_string()
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

    Some(format!("{RESOURCEPACK_THEMES_PATH}/{branch}/{theme_name}.ftml"))
}

/// Writes the theme boolean status to the temp file. When a theme include is matched,
/// `theme` is `true`; otherwise `false`. All other fields are left as
/// `null` / `[]` placeholders for later population.
///
/// ---
///
/// Tip: Only write `theme` boolean and full all others `null` or `[]`.
fn write_theme_boolean_status(matched: bool) {
    let status = ThemeStatus {
        theme: matched,
        theme_name: None,
        parent_theme: None,
        parent_theme_name: Vec::new(),
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
}
