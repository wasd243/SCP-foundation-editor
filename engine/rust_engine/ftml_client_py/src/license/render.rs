use super::model::{LicenseData, LicenseFileData};

fn escape_html(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}

fn render_file_entry(file: &LicenseFileData) -> String {
    format!(
        r#"<div class="file-entry"><button class="btn-del-file" onclick="this.parentElement.remove()">×</button><div class="license-field-row"><span class="field-label">文件名：</span><span class="editable-field" data-field="file_name" contenteditable="true">{file_name}</span></div><div class="license-field-row"><span class="field-label">图像名：</span><span class="editable-field" data-field="img_name" contenteditable="true">{img_name}</span></div><div class="license-field-row"><span class="field-label">图像作者：</span><span class="editable-field" data-field="img_author" contenteditable="true">{img_author}</span></div><div class="license-field-row"><span class="field-label">授权协议：</span><span class="editable-field" data-field="img_license" contenteditable="true">{img_license}</span></div><div class="license-field-row license-link-row"><span class="field-label">来源链接：</span><span class="editable-field" data-field="source_link" contenteditable="false" onclick="editLicenseLink(this)">{source_link}</span></div><div class="license-field-row"><span class="field-label">衍生自：</span><span class="editable-field" data-field="derived_from" contenteditable="true" style="word-break: break-all;">{derived_from}</span></div><div class="license-field-row"><span class="field-label">备注：</span><span class="editable-field" data-field="note" contenteditable="true">{note}</span></div></div>"#,
        file_name = escape_html(&file.file_name),
        img_name = escape_html(&file.img_name),
        img_author = escape_html(&file.img_author),
        img_license = escape_html(&file.img_license),
        source_link = escape_html(&file.source_link),
        derived_from = escape_html(&file.derived_from),
        note = escape_html(&file.note),
    )
}

pub fn render_html(data: &LicenseData) -> String {
    let files_html = data
        .files
        .iter()
        .map(render_file_entry)
        .collect::<Vec<_>>()
        .join("");

    let orig_attr = if data.is_original { "true" } else { "false" };
    let orig_btn_cls = if data.is_original { " active" } else { "" };
    let trans_row_cls = if data.is_original { " disabled" } else { "" };

    format!(
        r#"<div class="scp-component license-box open" data-type="license" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-original="{orig_attr}" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)<button class="btn-license-original{orig_btn_cls}" onclick="toggleLicenseOriginal(this, event)" title="原创：生成|lang=CN，并取消|translator">原创</button></div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true">{author}</span></div><div class="license-field-row license-translator-row{trans_row_cls}"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true">{translator}</span></div><hr><div class="extra-files-container">{files_html}</div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>"#,
        author = escape_html(&data.author),
        translator = escape_html(&data.translator),
        files_html = files_html,
        orig_attr = orig_attr,
        orig_btn_cls = orig_btn_cls,
        trans_row_cls = trans_row_cls,
    )
}
