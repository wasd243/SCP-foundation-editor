use similar::{ChangeTag, TextDiff};

pub(super) struct MergeDiff {
    pub(super) patch: String,
    pub(super) final_output: String,
}

pub(super) fn diff(origin: &str, output: &str) -> MergeDiff {
    let diff = TextDiff::from_lines(origin, output);
    let patch = diff
        .unified_diff()
        .header("@origin.ftml", "@output.ftml")
        .to_string();
    let final_output = patch_origin(&diff);

    MergeDiff {
        patch,
        final_output,
    }
}

fn patch_origin(diff: &TextDiff<'_, '_, str>) -> String {
    let mut output = String::new();

    for change in diff.iter_all_changes() {
        match change.tag() {
            ChangeTag::Delete => {}
            ChangeTag::Equal | ChangeTag::Insert => output.push_str(change.value()),
        }
    }

    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn patches_origin_into_output() {
        let origin = "a\nb\nc\n";
        let output = "a\nB\nc\nd\n";

        let diff = diff(origin, output);

        assert_eq!(diff.final_output, output);
        assert!(diff.patch.contains("--- @origin.ftml"));
        assert!(diff.patch.contains("+++ @output.ftml"));
    }
}
