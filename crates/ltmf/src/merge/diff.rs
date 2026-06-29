use similar::TextDiff;

/// Unified line diff between the cached origin and the exporter output, used only
/// for the `patch_origin.ftml` debug artifact. The final output is rebuilt by
/// `insert_ignore_lines::splice`, which also handles ignored-line re-insertion.
pub(super) fn diff(origin: &str, output: &str) -> String {
    TextDiff::from_lines(origin, output)
        .unified_diff()
        .header("@origin.ftml", "@output.ftml")
        .to_string()
}

#[cfg(test)]
mod tests {
    use super::diff;

    #[test]
    fn produces_unified_headers() {
        let patch = diff("a\nb\nc\n", "a\nB\nc\nd\n");
        assert!(patch.contains("--- @origin.ftml"));
        assert!(patch.contains("+++ @output.ftml"));
    }
}
