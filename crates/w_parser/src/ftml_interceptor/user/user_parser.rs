use regex::Regex;

pub fn parse_user(text: &str) -> String {
    // Identify content inside ~_WJ_USER_PARSER_BEGIN_~
    let re = Regex::new(r"(?is)~_WJ_USER_PARSER_BEGIN_~(.*?)~_WJ_USER_PARSER_END_~").unwrap();

    if !re.is_match(text) {
        return text.into();
    }

    re.replace_all(text, |captures: &regex::Captures| {
        let content = captures.get(1).map_or("", |matched| matched.as_str());
        format!(
            r#"<span class="wj-user" data-editor-export="user" data-editor-user="{content}">{content}</span>"#
        )
    })
    .into_owned()
}

pub fn parse_user_with_img(text: &str) -> String {
    // Identify content inside ~_WJ_USER_WITH_IMG_PARSER_BEGIN_~
    let re =
        Regex::new(r"(?is)~_WJ_USER_WITH_IMG_PARSER_BEGIN_~(.*?)~_WJ_USER_WITH_IMG_PARSER_END_~")
            .unwrap();

    if !re.is_match(text) {
        return text.into();
    }

    re.replace_all(text, |captures: &regex::Captures| {
        let content = captures.get(1).map_or("", |matched| matched.as_str());
        format!(
            r#"<span class="wj-user-with-img" data-editor-export="user-with-img" data-editor-user="{content}">{content}</span>"#
        )
    })
    .into_owned()
}
