use html_escape::encode_text;

pub(crate) use crate::aim::model::AimModel;

pub fn from_fields(
    blocks: &str,
    xxxx: &str,
    lv: &str,
    cc: &str,
    dc: &str,
    site: &str,
    dir: &str,
    head: &str,
    mtf: &str,
) -> AimModel {
    AimModel {
        blocks: encode_text(blocks).into_owned(),
        xxxx: encode_text(xxxx).into_owned(),
        lv: encode_text(lv).into_owned(),
        cc: encode_text(cc).into_owned(),
        dc: encode_text(dc).into_owned(),
        site: encode_text(site).into_owned(),
        dir: encode_text(dir).into_owned(),
        head: encode_text(head).into_owned(),
        mtf: encode_text(mtf).into_owned(),
    }
}

pub fn to_wikidot(model: &AimModel) -> String {
    let mut code =
        String::from("[[include :scp-wiki-cn:component:advanced-information-methodology\n");

    if !model.blocks.is_empty() {
        code.push_str(&format!("|blocks={}\n", model.blocks));
    }

    code.push_str("|lang=CN\n");

    if model.blocks != "!" {
        code.push_str(&format!(
            "|XXXX={}\n|lv={}\n|cc={}\n|dc={}\n",
            model.xxxx, model.lv, model.cc, model.dc
        ));
    }

    if model.blocks != "-" {
        code.push_str(&format!(
            "|site={}\n|dir={}\n|head={}\n|mtf={}\n",
            model.site, model.dir, model.head, model.mtf
        ));
    }

    code.push_str("]]\n");
    code
}
