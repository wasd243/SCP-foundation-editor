mod diff;
mod get_origin_cache;
mod get_output_cache;

use std::fs;
use std::io;

use diff::diff;
use get_origin_cache::get_origin_cache;
use get_output_cache::get_output_cache;

const FINAL_OUTPUT_PATH: &str =
    concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/final_output.ftml");
const PATCH_OUTPUT_PATH: &str =
    concat!(env!("CARGO_MANIFEST_DIR"), "/../../temp/patch_origin.ftml");

/// Merge exporter output with the cached origin and write the final output.
pub fn merge_final_output(output: String) -> Result<String, io::Error> {
    let origin = get_origin_cache()?;
    let output = get_output_cache(&output)?;
    let diff = diff(&origin, &output);
    let final_output = diff.final_output;

    fs::write(PATCH_OUTPUT_PATH, diff.patch)?;
    fs::write(FINAL_OUTPUT_PATH, &final_output)?;
    Ok(final_output)
}
