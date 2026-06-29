//! Splice user-ignored source lines back into the exported output via the diff.
//!
//! The parse side removes the ignored lines entirely, so they show up as `Delete`
//! changes when diffing `origin` against `output`. For each ignored line we keep
//! the `Delete` (i.e. re-insert the original text) at the position the diff aligns
//! it to, and record its new 1-based line number in the final output. The new
//! numbers are handed to `update_ignore_lines`, which rewrites the saved config.
//!
//! Tokens come from `config_dir()/ignore_lines.json` (e.g. `1-10` / `15`).

use std::collections::{BTreeMap, HashSet};

use similar::{ChangeTag, TextDiff};

use crate::paths::read_ignore_lines;

/// Splice the ignored lines back into `output` using the diff against `origin`.
/// Returns the final text plus a map of `origin line number → final line number`
/// for each ignored line. An empty `ranges` just rebuilds the output.
pub(super) fn insert_ignore_lines(
    origin: &str,
    output: &str,
    ranges: &[(usize, usize)],
) -> (String, BTreeMap<usize, usize>) {
    splice(origin, output, ranges)
}

/// Pure core. Walks the line diff; non-ignored changes follow the usual
/// "keep output, drop deletions" rebuild, while ignored deletions are re-inserted
/// (the original line) and their new position recorded.
fn splice(
    origin: &str,
    output: &str,
    ranges: &[(usize, usize)],
) -> (String, BTreeMap<usize, usize>) {
    let ignored: HashSet<usize> = ranges.iter().flat_map(|&(s, e)| s..=e).collect();
    let diff = TextDiff::from_lines(origin, output);

    let mut final_output = String::new();
    let mut new_positions = BTreeMap::new();
    let mut line_no = 0usize; // lines emitted into final_output so far

    for change in diff.iter_all_changes() {
        match change.tag() {
            ChangeTag::Equal | ChangeTag::Insert => {
                final_output.push_str(change.value());
                line_no += 1;
            }
            ChangeTag::Delete => {
                let origin_line = change.old_index().expect("delete change has an old index") + 1;
                if ignored.contains(&origin_line) {
                    final_output.push_str(change.value());
                    line_no += 1;
                    new_positions.insert(origin_line, line_no);
                }
                // Non-ignored deletions are dropped (kept the output's version).
            }
        }
    }

    (final_output, new_positions)
}

/// Read the saved tokens from `config/ignore_lines.json` and parse them into
/// ranges. A missing/empty file means "nothing ignored". Shared with `merge.rs`.
pub(super) fn read_ignore_ranges() -> Vec<(usize, usize)> {
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
    use super::{parse_token, splice};

    #[test]
    fn splices_removed_line_back() {
        // Parse side removed line 2 ("b"); the diff re-inserts it.
        let origin = "a\nb\nc\n";
        let output = "a\nc\n";
        let (final_output, map) = splice(origin, output, &[(2, 2)]);
        assert_eq!(final_output, "a\nb\nc\n");
        assert_eq!(map.get(&2), Some(&2));
    }

    #[test]
    fn splices_back_at_drifted_position() {
        // User prepended "intro" and the ignored line 2 was removed at parse time.
        let origin = "alpha\nIGNORED\nbeta\n";
        let output = "intro\nalpha\nbeta\n";
        let (final_output, map) = splice(origin, output, &[(2, 2)]);
        assert_eq!(final_output, "intro\nalpha\nIGNORED\nbeta\n");
        // origin line 2 now lands on final line 3.
        assert_eq!(map.get(&2), Some(&3));
    }

    #[test]
    fn empty_ranges_rebuild_output() {
        let origin = "a\nb\n";
        let output = "a\nB\n";
        let (final_output, map) = splice(origin, output, &[]);
        assert_eq!(final_output, "a\nB\n");
        assert!(map.is_empty());
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
