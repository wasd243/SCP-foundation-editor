use std::fs;
use std::io;

use crate::ftml_fmt::output_path;

pub(super) fn get_output_cache(output: &str) -> Result<String, io::Error> {
    let output = fs::read_to_string(output_path()).unwrap_or_else(|_| output.to_string());
    Ok(output)
}
