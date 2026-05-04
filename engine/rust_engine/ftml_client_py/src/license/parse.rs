use regex::Regex;

use super::model::{LicenseData, LicenseFileData};

fn get_arg(source: &str, name: &str) -> String {
    let pattern = format!(r"(?i)\|{}\s*=\s*([^\|\n\]]+)", regex::escape(name));
    Regex::new(&pattern)
        .unwrap()
        .captures(source)
        .and_then(|caps| caps.get(1))
        .map(|m| m.as_str().trim().to_string())
        .unwrap_or_default()
}

fn parse_files(source: &str) -> Vec<LicenseFileData> {
    let Some(files_block) = Regex::new(r"(?is)=====(.*?)=====")
        .unwrap()
        .captures(source)
        .and_then(|caps| caps.get(1))
        .map(|m| m.as_str().trim().to_string())
    else {
        return Vec::new();
    };

    let mut files = Vec::new();
    let mut current = LicenseFileData {
        file_name: String::new(),
        img_name: String::new(),
        img_author: String::new(),
        img_license: String::new(),
        source_link: String::new(),
        derived_from: String::new(),
        note: String::new(),
    };

    let flush = |current: &mut LicenseFileData, files: &mut Vec<LicenseFileData>| {
        if !current.file_name.is_empty()
            || !current.img_name.is_empty()
            || !current.img_author.is_empty()
            || !current.img_license.is_empty()
            || !current.source_link.is_empty()
            || !current.derived_from.is_empty()
            || !current.note.is_empty()
        {
            files.push(current.clone());
            *current = LicenseFileData {
                file_name: String::new(),
                img_name: String::new(),
                img_author: String::new(),
                img_license: String::new(),
                source_link: String::new(),
                derived_from: String::new(),
                note: String::new(),
            };
        }
    };

    for raw_line in files_block.lines() {
        let line = raw_line.trim();
        if !line.starts_with('>') {
            continue;
        }
        let content = line[1..].trim();
        if content.starts_with("**文件名：**") {
            flush(&mut current, &mut files);
            current.file_name = content.replace("**文件名：**", "").trim().to_string();
        } else if content.starts_with("**图像名：**") {
            current.img_name = content.replace("**图像名：**", "").trim().to_string();
        } else if content.starts_with("**图像作者：**") {
            current.img_author = content.replace("**图像作者：**", "").trim().to_string();
        } else if content.starts_with("**作者：**") {
            current.img_author = content.replace("**作者：**", "").trim().to_string();
        } else if content.starts_with("**授权协议：**") {
            current.img_license = content.replace("**授权协议：**", "").trim().to_string();
        } else if content.starts_with("**来源链接：**") {
            current.source_link = content.replace("**来源链接：**", "").trim().to_string();
        } else if content.starts_with("来源链接：") {
            current.source_link = content.replace("来源链接：", "").trim().to_string();
        } else if content.starts_with("**衍生自：**") {
            current.derived_from = content.replace("**衍生自：**", "").trim().to_string();
        } else if content.starts_with("**备注：**") {
            current.note = content.replace("**备注：**", "").trim().to_string();
        }
    }
    flush(&mut current, &mut files);

    files
}

pub fn parse_license_data(source: &str) -> LicenseData {
    LicenseData {
        // source: source.to_string(),
        author: get_arg(source, "author"),
        translator: get_arg(source, "translator"),
        is_original: Regex::new(r"(?i)\|lang=CN")
            .unwrap()
            .is_match(source),
        files: parse_files(source),
    }
}
