//! Remove user-ignored source lines before FTML tokenization.
//!
//! The user marks line numbers/ranges as "ignored" in settings, persisted to
//! `config_dir()/ignore_lines.json` (tokens like `1-10` / `15`). For each ignored
//! line we drop the whole line, so FTML never parses that (possibly fragile)
//! content and the editor never shows it. The exporter's merge later finds these
//! removed lines in the diff against `origin.ftml`, splices the originals back at
//! their new positions, and updates the saved line numbers. A missing ignore file
//! is a no-op.
//!
//! Runs on the raw source, before `ftml::preprocess` and include expansion, so
//! the line numbers line up with `origin.ftml`.

use std::collections::HashSet;

use crate::paths::read_ignore_lines;

/// Remove the user-ignored lines from `wikitext`.
pub fn user_ignore_interceptor(wikitext: &str) -> String {
    let ranges = read_ignore_ranges();
    if ranges.is_empty() {
        return wikitext.to_string();
    }
    remove_lines(wikitext, &ranges)
}

/// Pure core: drop every line whose 1-based number falls in an inclusive range.
/// Split/join on `'\n'` so a trailing newline round-trips; lines beyond the text
/// are simply never matched.
fn remove_lines(wikitext: &str, ranges: &[(usize, usize)]) -> String {
    let ignored: HashSet<usize> = ranges.iter().flat_map(|&(start, end)| start..=end).collect();

    wikitext
        .split('\n')
        .enumerate()
        .filter(|(i, _)| !ignored.contains(&(i + 1)))
        .map(|(_, line)| line)
        .collect::<Vec<_>>()
        .join("\n")
}

/// Read the saved tokens from `config/ignore_lines.json` and parse them into
/// ranges. A missing/empty file means "nothing ignored".
fn read_ignore_ranges() -> Vec<(usize, usize)> {
    read_ignore_lines()
        .iter()
        .filter_map(|token| parse_token(token))
        .collect()
}

/// Parse a single token: `N` → `(n, n)`, `X-Y` → `(x, y)`. Defensively rejects
/// non-numeric, `< 1`, or `y < x` (tokens are already validated when saved).
fn parse_token(token: &str) -> Option<(usize, usize)> {
    let token = token.trim();
    if token.is_empty() {
        return None;
    }

    match token.split_once('-') {
        Some((start, end)) => {
            let start = start.trim().parse::<usize>().ok()?;
            let end = end.trim().parse::<usize>().ok()?;
            (start >= 1 && end >= start).then_some((start, end))
        }
        None => {
            let n = token.parse::<usize>().ok()?;
            (n >= 1).then_some((n, n))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{parse_token, remove_lines};

    #[test]
    fn removes_single_line() {
        let text = "alpha\n[[bad]]raw[[/bad]]\ngamma\n";
        assert_eq!(remove_lines(text, &[(2, 2)]), "alpha\ngamma\n");
    }

    #[test]
    fn removes_a_range() {
        let text = "a\nb\nc\nd\n";
        assert_eq!(remove_lines(text, &[(2, 3)]), "a\nd\n");
    }

    #[test]
    fn skips_out_of_range_lines() {
        let text = "a\nb\n";
        assert_eq!(remove_lines(text, &[(9, 9)]), "a\nb\n");
    }

    #[test]
    fn parses_singles_and_ranges() {
        assert_eq!(parse_token("7"), Some((7, 7)));
        assert_eq!(parse_token("1-10"), Some((1, 10)));
        assert_eq!(parse_token(" 3 - 5 "), Some((3, 5)));
    }

    #[test]
    fn rejects_malformed_tokens() {
        assert_eq!(parse_token("abc"), None);
        assert_eq!(parse_token("0"), None);
        assert_eq!(parse_token("10-1"), None);
        assert_eq!(parse_token(""), None);
    }
}
