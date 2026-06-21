mod diff;
mod get_origin_cache;
mod get_output_cache;

use std::fs;
use std::io;

use diff::diff;
use get_origin_cache::get_origin_cache;
use get_output_cache::get_output_cache;

use crate::paths::temp_dir;

/// Merge exporter output with the cached origin and write the final output.
pub fn merge_final_output(output: String) -> Result<String, io::Error> {
    let origin = get_origin_cache()?;
    let output = get_output_cache(&output)?;
    let diff = diff(&origin, &output);
    let final_output = diff.final_output;

    let cache_dir = temp_dir();
    fs::write(cache_dir.join("patch_origin.ftml"), diff.patch)?;
    fs::write(cache_dir.join("final_output.ftml"), &final_output)?;
    Ok(final_output)
}
