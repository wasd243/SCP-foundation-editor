use super::model::{LicenseData, LicenseFileData};
use html_escape::encode_text;

fn render_file_entry(file: &LicenseFileData) -> String {
    let file_name = encode_text(&file.file_name);
    let img_name = encode_text(&file.img_name);
    let img_author = encode_text(&file.img_author);
    let img_license = encode_text(&file.img_license);
    let source_link = encode_text(&file.source_link);
    let derived_from = encode_text(&file.derived_from);
    let note = encode_text(&file.note);

    format!(
        r#"<div class="file-entry"><button class="btn-del-file" onclick="this.parentElement.remove()">×</button><div class="license-field-row"><span class="field-label">文件名：</span><span class="editable-field" data-field="file_name" contenteditable="true">{file_name}</span></div><div class="license-field-row"><span class="field-label">图像名：</span><span class="editable-field" data-field="img_name" contenteditable="true">{img_name}</span></div><div class="license-field-row"><span class="field-label">图像作者：</span><span class="editable-field" data-field="img_author" contenteditable="true">{img_author}</span></div><div class="license-field-row"><span class="field-label">授权协议：</span><span class="editable-field" data-field="img_license" contenteditable="true">{img_license}</span></div><div class="license-field-row license-link-row"><span class="field-label">来源链接：</span><span class="editable-field" data-field="source_link" contenteditable="false" onclick="editLicenseLink(this)">{source_link}</span></div><div class="license-field-row"><span class="field-label">衍生自：</span><span class="editable-field" data-field="derived_from" contenteditable="true" style="word-break: break-all;">{derived_from}</span></div><div class="license-field-row"><span class="field-label">备注：</span><span class="editable-field" data-field="note" contenteditable="true">{note}</span></div></div>"#,
        file_name = file_name,
        img_name = img_name,
        img_author = img_author,
        img_license = img_license,
        source_link = source_link,
        derived_from = derived_from,
        note = note,
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

    let author = encode_text(&data.author);
    let translator = encode_text(&data.translator);

    format!(
        r#"<div class="scp-component license-box open" data-type="license" data-source-uuid="{{{{uuid}}}}" data-source="{{{{source}}}}" data-original="{orig_attr}" contenteditable="false"><div class="license-header">授权/引用信息 (点击展开/折叠)<button class="btn-license-original{orig_btn_cls}" onclick="toggleLicenseOriginal(this, event)" title="原创：生成|lang=CN，并取消|translator">原创</button></div><div class="license-content"><div class="license-field-row"><span class="field-label">作者：</span><span class="editable-field" data-field="author" contenteditable="true">{author}</span></div><div class="license-field-row license-translator-row{trans_row_cls}"><span class="field-label">译者：</span><span class="editable-field" data-field="translator" contenteditable="true">{translator}</span></div><hr><div class="extra-files-container">{files_html}</div><button class="btn-add-file" onclick="addLicenseFile(this)">+ 新增文件</button></div></div>"#,
        author = author,
        translator = translator,
        files_html = files_html,
        orig_attr = orig_attr,
        orig_btn_cls = orig_btn_cls,
        trans_row_cls = trans_row_cls,
    )
}
