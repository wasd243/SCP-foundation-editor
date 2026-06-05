mod fmt_newline;

pub fn ftml_fmt(ftml: &str) -> String {
    fmt_newline::format_newline(ftml)
}
