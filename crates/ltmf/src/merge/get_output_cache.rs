use std::fs;
use std::io;

use crate::ftml_fmt::OUTPUT_PATH;

pub(super) fn get_output_cache(output: &str) -> Result<String, io::Error> {
    let output = fs::read_to_string(OUTPUT_PATH).unwrap_or_else(|_| output.to_string());
    Ok(output)
}
