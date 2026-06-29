//! Update the saved ignored-line numbers after the exporter splices the ignored
//! lines back into the final output.
//!
//! `insert_ignore_lines` reports where each ignored origin line landed in the
//! final output (its new 1-based number). We rewrite each saved range with those
//! numbers, keeping the token shape: a single line stays a single number, a
//! contiguous range stays `x-y`. A range whose lines aren't all present in this
//! export (e.g. the setting changed but the doc wasn't re-parsed, or that section
//! isn't in the current document) keeps its original numbers untouched. Only a
//! genuinely impossible case — a fully-mapped range that came back
//! non-contiguous — panics, with no Result fallback.

use std::collections::BTreeMap;

use crate::paths::write_ignore_lines;

/// Rewrite `config/ignore_lines.json` so the saved ranges point at the ignored
/// lines' new positions. No-op when there were no ignored ranges, so we never
/// clobber the config with an empty list.
pub(super) fn update_ignore_lines(
    ranges: &[(usize, usize)],
    new_positions: &BTreeMap<usize, usize>,
) {
    if ranges.is_empty() || new_positions.is_empty() {
        // Nothing was spliced back this export (no ignored ranges, or none of them
        // are in the current document), so there is no line number to update.
        return;
    }

    let tokens: Vec<String> = ranges
        .iter()
        .map(|&(start, end)| {
            range_to_token(start, end, new_positions).unwrap_or_else(|e| panic!("{e}"))
        })
        .collect();

    write_ignore_lines(&tokens);
}

/// Map one saved range onto its new token using the post-splice positions.
/// Single line → single number; contiguous range → `x-y`. If any line in the
/// range has no new position (the range isn't in this export), the original token
/// is kept. Returns `Err` only for a fully-mapped range that came back
/// non-contiguous, which the caller turns into a panic.
fn range_to_token(
    start: usize,
    end: usize,
    new_positions: &BTreeMap<usize, usize>,
) -> Result<String, String> {
    let original = if start == end {
        start.to_string()
    } else {
        format!("{start}-{end}")
    };

    // Every line must have a new position to update; otherwise keep it as-is.
    let Some(new) = (start..=end)
        .map(|line| new_positions.get(&line).copied())
        .collect::<Option<Vec<usize>>>()
    else {
        return Ok(original);
    };

    if start == end {
        return Ok(new[0].to_string());
    }

    // Multi-line range: the new positions must stay contiguous.
    for pair in new.windows(2) {
        if pair[1] != pair[0] + 1 {
            return Err(format!(
                "ignored range {start}-{end} became non-contiguous after export: {new:?}"
            ));
        }
    }
    Ok(format!("{}-{}", new[0], new[new.len() - 1]))
}

#[cfg(test)]
mod tests {
    use super::range_to_token;
    use std::collections::BTreeMap;

    fn map(pairs: &[(usize, usize)]) -> BTreeMap<usize, usize> {
        pairs.iter().copied().collect()
    }

    #[test]
    fn single_line_maps_to_single_number() {
        let m = map(&[(2, 5)]);
        assert_eq!(range_to_token(2, 2, &m).unwrap(), "5");
    }

    #[test]
    fn contiguous_range_stays_a_range() {
        let m = map(&[(3, 7), (4, 8), (5, 9)]);
        assert_eq!(range_to_token(3, 5, &m).unwrap(), "7-9");
    }

    #[test]
    fn non_contiguous_range_errs() {
        let m = map(&[(3, 7), (4, 9), (5, 10)]);
        assert!(range_to_token(3, 5, &m).is_err());
    }

    #[test]
    fn missing_mapping_keeps_original_token() {
        let m = map(&[(3, 7)]); // lines 4 and 5 have no new position
        assert_eq!(range_to_token(3, 5, &m).unwrap(), "3-5");
    }

    #[test]
    fn missing_single_keeps_original() {
        let m = map(&[]);
        assert_eq!(range_to_token(8, 8, &m).unwrap(), "8");
    }
}
