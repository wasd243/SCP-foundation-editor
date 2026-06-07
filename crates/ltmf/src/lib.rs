mod ftml_fmt;
mod import_json;
mod interpret;
mod merge;
mod preprocess;

pub use ftml_fmt::ftml_fmt;
pub use interpret::interpret;
pub use merge::merge_final_output;
pub use preprocess::preprocess;

pub fn export_wikitext(json: &str) -> Result<String, String> {
    let json = preprocess(json)?;
    let json = interpret(&json)?;
    let json = ftml_fmt(&json);
    merge_final_output(json).map_err(|error| error.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_export() {
        export_wikitext("").unwrap();
    }

    // fn test_export_default_json() {
    //     let json = export_wikitext("").unwrap();
    //     let default_path = concat!(env!("CARGO_MANIFEST_DIR"), "/test/json/default.json");
    //
    //     fs::write(default_path, &json).unwrap();
    //     write_normalize_archive_if_changed(&json);
    //
    //     println!("Pass");
    // }
    //
    // fn write_normalize_archive_if_changed(json: &str) {
    //     let normalize_dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("test/json/normalize");
    //     fs::create_dir_all(&normalize_dir).unwrap();
    //
    //     let (latest_number, latest_path) = latest_normalize_archive(&normalize_dir);
    //
    //     if let Some(path) = latest_path {
    //         let latest_json = fs::read_to_string(path).unwrap();
    //         if same_json(&latest_json, json) {
    //             return;
    //         }
    //     }
    //
    //     let next_path = normalize_dir.join(format!("normalize_{}.json", latest_number + 1));
    //     fs::write(next_path, json).unwrap();
    // }
    //
    // fn latest_normalize_archive(normalize_dir: &Path) -> (usize, Option<PathBuf>) {
    //     fs::read_dir(normalize_dir)
    //         .unwrap()
    //         .filter_map(Result::ok)
    //         .filter_map(|entry| {
    //             let path = entry.path();
    //             let number = path
    //                 .file_stem()
    //                 .and_then(|stem| stem.to_str())
    //                 .and_then(|stem| stem.strip_prefix("normalize_"))
    //                 .and_then(|number| number.parse::<usize>().ok())?;
    //
    //             Some((number, path))
    //         })
    //         .max_by_key(|(number, _)| *number)
    //         .map_or((0, None), |(number, path)| (number, Some(path)))
    // }
    //
    // fn same_json(left: &str, right: &str) -> bool {
    //     let left_json = serde_json::from_str::<serde_json::Value>(left);
    //     let right_json = serde_json::from_str::<serde_json::Value>(right);
    //
    //     match (left_json, right_json) {
    //         (Ok(left_json), Ok(right_json)) => left_json == right_json,
    //         _ => left == right,
    //     }
    // }
}
