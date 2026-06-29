mod diff;
mod get_origin_cache;
mod get_output_cache;
mod insert_ignore_lines;
mod update_ignore_lines;

use std::fs;
use std::io;

use diff::diff;
use get_origin_cache::get_origin_cache;
use get_output_cache::get_output_cache;
use insert_ignore_lines::{insert_ignore_lines, read_ignore_ranges};
use update_ignore_lines::update_ignore_lines;

use crate::paths::temp_dir;

/// Merge exporter output with the cached origin and write the final output.
///
/// `origin.ftml` is the baseline for the diff. It alternates owners: `parse_wikidot`
/// writes the raw source on parse, and this function rewrites it to the just-built
/// final output on export, so the next diff and the updated ignore-line config stay
/// in one line-number space.
pub fn merge_final_output(output: String) -> Result<String, io::Error> {
    let origin = get_origin_cache()?;
    let output = get_output_cache(&output)?;

    // Splice the ignored source lines back in via the diff, then update the saved
    // line numbers to where they landed in the final output.
    let ranges = read_ignore_ranges();
    let (final_output, new_positions) = insert_ignore_lines(&origin, &output, &ranges);
    update_ignore_lines(&ranges, &new_positions);

    let cache_dir = temp_dir();
    fs::write(cache_dir.join("patch_origin.ftml"), diff(&origin, &output))?;
    fs::write(cache_dir.join("final_output.ftml"), &final_output)?;

    // "Export becomes the new source": rebase origin.ftml onto this export so the
    // next diff and the just-updated config/ignore_lines.json share one line-number
    // space. parse_wikidot still re-seeds origin.ftml from the source on the next
    // code-view/import edit; this only covers the WYSIWYG-onUpdate / autosave
    // export paths that never round-trip through the code view.
    fs::write(cache_dir.join("origin.ftml"), &final_output)?;

    Ok(final_output)
}
