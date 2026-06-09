use regex::Regex;

pub fn user_interceptor(text: &str) -> String {
    let re = Regex::new(r"(?i)\[\[user\s+(.+?)\]\]").unwrap();

    re.replace_all(text, "~_WJ_USER_PARSER_BEGIN_~$1~_WJ_USER_PARSER_END_~")
        .into_owned()
}

pub fn user_with_img_interceptor(text: &str) -> String {
    let re = Regex::new(r"(?i)\[\[\*user\s+(.+?)\]\]").unwrap();

    re.replace_all(
        text,
        "~_WJ_USER_WITH_IMG_PARSER_BEGIN_~$1~_WJ_USER_WITH_IMG_PARSER_END_~",
    )
    .into_owned()
}
